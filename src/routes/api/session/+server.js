import { json } from '@sveltejs/kit';

// In-memory store for active sessions (persists while the dev server is running)
// Map structure: userId -> activeSessionId
const activeSessions = new Map();

export async function POST({ request }) {
    try {
        const { userId, sessionId } = await request.json();
        
        if (!userId || !sessionId) {
            return json({ success: false, error: 'Missing userId or sessionId' }, { status: 400 });
        }
        
        // Register the new session as the ONLY active session for this user
        activeSessions.set(userId, sessionId);
        
        return json({ success: true, activeSession: sessionId });
    } catch (error) {
        return json({ success: false, error: 'Invalid request' }, { status: 400 });
    }
}

export async function GET({ url }) {
    const userId = url.searchParams.get('userId');
    
    if (!userId) {
        return json({ success: false, error: 'Missing userId' }, { status: 400 });
    }

    const activeSession = activeSessions.get(userId) || null;
    return json({ success: true, activeSession });
}
