/* ═══════════════════════════════════════════════════════════════
   IRONPLAN 70.3 — Express Server
   Static file serving + Strava OAuth backend
   Production-ready for Render.com deployment
   ═══════════════════════════════════════════════════════════════ */

require('dotenv').config();
const express = require('express');
const axios = require('axios');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;
const BASE_URL = process.env.BASE_URL || `http://localhost:${PORT}`;

const STRAVA_CLIENT_ID = process.env.STRAVA_CLIENT_ID;
const STRAVA_CLIENT_SECRET = process.env.STRAVA_CLIENT_SECRET;
const REDIRECT_URI = `${BASE_URL}/auth/strava/callback`;

// ── Middleware ─────────────────────────────────────────────────
app.use(express.static(path.join(__dirname, '/'), {
    maxAge: process.env.NODE_ENV === 'production' ? '1d' : 0,
    etag: true,
}));
app.use(express.json());

// Security headers
app.use((req, res, next) => {
    res.setHeader('X-Content-Type-Options', 'nosniff');
    res.setHeader('X-Frame-Options', 'DENY');
    res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
    next();
});

// ── Strava OAuth: Initiate ────────────────────────────────────
app.get('/auth/strava', (req, res) => {
    if (!STRAVA_CLIENT_ID || STRAVA_CLIENT_ID === 'your_client_id_here') {
        return res.status(400).json({
            error: 'Strava not configured',
            message: 'Please set STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET in your .env file. Visit https://www.strava.com/settings/api to create an app.'
        });
    }
    const scope = 'activity:read_all,profile:read_all';
    const authUrl = `https://www.strava.com/oauth/authorize?client_id=${STRAVA_CLIENT_ID}&redirect_uri=${encodeURIComponent(REDIRECT_URI)}&response_type=code&scope=${scope}&approval_prompt=auto`;
    res.redirect(authUrl);
});

// ── Strava OAuth: Callback ───────────────────────────────────
app.get('/auth/strava/callback', async (req, res) => {
    const { code, error } = req.query;
    if (error) {
        return res.redirect('/?strava_error=' + encodeURIComponent(error));
    }
    if (!code) {
        return res.redirect('/?strava_error=no_code');
    }
    try {
        const response = await axios.post('https://www.strava.com/oauth/token', {
            client_id: STRAVA_CLIENT_ID,
            client_secret: STRAVA_CLIENT_SECRET,
            code: code,
            grant_type: 'authorization_code'
        });

        const { access_token, refresh_token, expires_at, athlete } = response.data;
        // Return an HTML page that stores tokens in localStorage and redirects
        res.send(`<!DOCTYPE html>
<html><head><title>Connecting to Strava...</title></head>
<body style="background:#0a0a0f;color:#fff;font-family:Inter,sans-serif;display:flex;align-items:center;justify-content:center;height:100vh">
<div style="text-align:center">
<div style="font-size:2rem;margin-bottom:1rem">🔗</div>
<div>Connecting to Strava...</div>
<script>
localStorage.setItem('strava_token', '${access_token}');
localStorage.setItem('strava_refresh', '${refresh_token}');
localStorage.setItem('strava_expires', '${expires_at}');
localStorage.setItem('strava_athlete', '${JSON.stringify(athlete).replace(/'/g, "\\'")}');
localStorage.setItem('strava_connected', 'true');
setTimeout(function(){ window.location.href = '/?strava_connected=1'; }, 800);
</script>
</div></body></html>`);
    } catch (err) {
        console.error('Strava auth error:', err.response?.data || err.message);
        res.redirect('/?strava_error=' + encodeURIComponent(err.response?.data?.message || err.message));
    }
});

// ── Strava Token Refresh ──────────────────────────────────────
app.post('/api/strava/refresh', async (req, res) => {
    const { refresh_token } = req.body;
    if (!refresh_token) {
        return res.status(400).json({ error: 'Missing refresh_token' });
    }
    try {
        const response = await axios.post('https://www.strava.com/oauth/token', {
            client_id: STRAVA_CLIENT_ID,
            client_secret: STRAVA_CLIENT_SECRET,
            refresh_token: refresh_token,
            grant_type: 'refresh_token'
        });
        res.json(response.data);
    } catch (err) {
        console.error('Token refresh error:', err.response?.data || err.message);
        res.status(500).json({ error: err.response?.data?.message || err.message });
    }
});

// ── Strava API Proxy: Activities ──────────────────────────────
app.get('/api/strava/activities', async (req, res) => {
    const token = req.headers.authorization;
    if (!token) return res.status(401).json({ error: 'No authorization header' });

    try {
        const response = await axios.get('https://www.strava.com/api/v3/athlete/activities', {
            headers: { Authorization: token },
            params: {
                per_page: req.query.per_page || 50,
                page: req.query.page || 1,
                after: req.query.after || undefined,
                before: req.query.before || undefined
            }
        });
        res.json(response.data);
    } catch (err) {
        if (err.response?.status === 401) {
            return res.status(401).json({ error: 'Token expired', needsRefresh: true });
        }
        res.status(500).json({ error: err.response?.data?.message || err.message });
    }
});

// ── Strava API Proxy: Athlete Stats ───────────────────────────
app.get('/api/strava/athlete/stats', async (req, res) => {
    const token = req.headers.authorization;
    if (!token) return res.status(401).json({ error: 'No authorization header' });

    try {
        const athleteData = JSON.parse(req.headers['x-athlete-id'] || '{}');
        const athleteId = athleteData.id || req.query.athlete_id;
        if (!athleteId) return res.status(400).json({ error: 'No athlete ID' });

        const response = await axios.get(`https://www.strava.com/api/v3/athletes/${athleteId}/stats`, {
            headers: { Authorization: token }
        });
        res.json(response.data);
    } catch (err) {
        res.status(500).json({ error: err.response?.data?.message || err.message });
    }
});

// ── Strava API Proxy: Activity Detail ─────────────────────────
app.get('/api/strava/activities/:id', async (req, res) => {
    const token = req.headers.authorization;
    if (!token) return res.status(401).json({ error: 'No authorization header' });

    try {
        const response = await axios.get(`https://www.strava.com/api/v3/activities/${req.params.id}`, {
            headers: { Authorization: token }
        });
        res.json(response.data);
    } catch (err) {
        res.status(500).json({ error: err.response?.data?.message || err.message });
    }
});

// ── Check Strava Config Status ────────────────────────────────
app.get('/api/strava/status', (req, res) => {
    const configured = STRAVA_CLIENT_ID && STRAVA_CLIENT_ID !== 'your_client_id_here';
    res.json({ configured, redirectUri: REDIRECT_URI });
});

// ── Disconnect Strava ─────────────────────────────────────────
app.post('/api/strava/disconnect', async (req, res) => {
    const token = req.headers.authorization?.replace('Bearer ', '');
    if (token) {
        try {
            await axios.post('https://www.strava.com/oauth/deauthorize', null, {
                headers: { Authorization: `Bearer ${token}` }
            });
        } catch (err) {
            // Ignore deauth errors
        }
    }
    res.json({ success: true });
});

// ── Fallback: serve index.html ────────────────────────────────
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// ── Start Server ──────────────────────────────────────────────
app.listen(PORT, '0.0.0.0', () => {
    console.log(`\n  ⚡ IronPlan 70.3 running at ${BASE_URL}`);
    console.log(`  📊 Dashboard ready`);
    console.log(`  🌍 Environment: ${process.env.NODE_ENV || 'development'}\n`);
    if (!STRAVA_CLIENT_ID || STRAVA_CLIENT_ID === 'your_client_id_here') {
        console.log('  ⚠️  Strava not configured. Edit .env with your API credentials.');
        console.log('  📋 Get credentials at: https://www.strava.com/settings/api\n');
    } else {
        console.log(`  ✅ Strava OAuth configured (Client ID: ${STRAVA_CLIENT_ID})`);
        console.log(`  🔗 Callback URL: ${REDIRECT_URI}\n`);
    }
});
