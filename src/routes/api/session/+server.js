import { json } from '@sveltejs/kit';

/**
 * Temporary in-memory session store for single-device login during frontend development.
 * Backend integration point — replace with Django session / Redis when API is ready.
 */
const activeSessions = new Map();

/** Backend integration point */
export async function POST({ request }) {
  try {
    const { userId, sessionId } = await request.json();

    if (!userId || !sessionId) {
      return json({ success: false, error: 'Missing userId or sessionId' }, { status: 400 });
    }

    activeSessions.set(userId, sessionId);
    return json({ success: true, activeSession: sessionId });
  } catch {
    return json({ success: false, error: 'Invalid request' }, { status: 400 });
  }
}

/** Backend integration point */
export async function GET({ url }) {
  const userId = url.searchParams.get('userId');

  if (!userId) {
    return json({ success: false, error: 'Missing userId' }, { status: 400 });
  }

  const activeSession = activeSessions.get(userId) || null;
  return json({ success: true, activeSession });
}
