<script>
  /**
   * Public landing page (home route: /)
   *
   * - Visitors see product info and a link to sign in.
   * - Logged-in users are sent to their dashboard automatically.
   */
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { authStore } from '$lib/stores/auth.js';
  import {
    UtensilsCrossed,
    QrCode,
    Users,
    ScanLine,
    ArrowRight,
    CheckCircle2
  } from 'lucide-svelte';

  // If someone is already signed in, skip the marketing page
  onMount(() => {
    if (!$authStore.isAuthenticated) return;

    if ($authStore.role === 'admin') goto('/admin');
    else if ($authStore.role === 'scanner') goto('/scanner');
    else goto('/dashboard');
  });

  const features = [
    {
      title: 'QR meal access',
      description: 'Members generate a short-lived QR code on their phone and show it at the counter.',
      icon: QrCode
    },
    {
      title: 'Admin control',
      description: 'Manage users, meal packages, attendance logs, and bulk imports from one place.',
      icon: Users
    },
    {
      title: 'Fast scanning',
      description: 'Staff scan codes with a camera and see instant granted or denied feedback.',
      icon: ScanLine
    }
  ];

  const steps = [
    'Admin uploads members and sets breakfast, lunch, or dinner access.',
    'Members open the app and display their QR code during meal hours.',
    'Scanner staff verify attendance; logs are available for export.'
  ];
</script>

<svelte:head>
  <title>Meal Trackers — Simple meal access for your organization</title>
  <meta
    name="description"
    content="QR-based meal tracking for schools, camps, and workplaces. Easy for members, clear for admins."
  />
</svelte:head>

<div class="landing">
  <!-- Top navigation: stays visible while scrolling -->
  <header class="top-nav">
    <a href="/" class="brand">
      <span class="brand-mark" aria-hidden="true">
        <UtensilsCrossed size={22} />
      </span>
      <span>Meal Trackers</span>
    </a>
    <nav class="nav-links" aria-label="Main">
      <a href="#features">Features</a>
      <a href="#how-it-works">How it works</a>
      <a href="/login" class="btn btn-primary nav-cta">Sign in</a>
    </nav>
  </header>

  <main>
    <!-- Hero: first thing visitors read -->
    <section class="hero">
      <div class="hero-copy">
        <p class="eyebrow">Meal access made simple</p>
        <h1>Track meals with QR codes your team can actually use</h1>
        <p class="lead">
          Meal Trackers helps organizations manage who can eat breakfast, lunch, or dinner—without
          paper lists or long queues. Built as a modern web app you can connect to your own API later.
        </p>
        <div class="hero-actions">
          <a href="/login" class="btn btn-primary">
            Get started
            <ArrowRight size={18} />
          </a>
          <a href="#features" class="btn btn-outline">See features</a>
        </div>
      </div>

      <div class="hero-card" aria-hidden="true">
        <div class="mock-qr">
          <QrCode size={120} strokeWidth={1.25} />
        </div>
        <p class="mock-label">Live QR · refreshes every minute</p>
        <ul class="mock-stats">
          <li><CheckCircle2 size={16} /> Breakfast 07:00–09:30</li>
          <li><CheckCircle2 size={16} /> Lunch 12:30–14:30</li>
        </ul>
      </div>
    </section>

    <!-- Feature cards -->
    <section id="features" class="section">
      <header class="section-head">
        <h2>What you can do</h2>
        <p>Three roles, one system: members, administrators, and scanner staff.</p>
      </header>
      <div class="feature-grid">
        {#each features as item}
          {@const Icon = item.icon}
          <article class="feature-card">
            <div class="feature-icon">
              <Icon size={24} />
            </div>
            <h3>{item.title}</h3>
            <p>{item.description}</p>
          </article>
        {/each}
      </div>
    </section>

    <!-- Simple 3-step explanation for learners reading the markup -->
    <section id="how-it-works" class="section alt">
      <header class="section-head">
        <h2>How it works</h2>
        <p>A straightforward flow from setup to check-in.</p>
      </header>
      <ol class="steps">
        {#each steps as text, index}
          <li>
            <span class="step-num">{index + 1}</span>
            <p>{text}</p>
          </li>
        {/each}
      </ol>
    </section>

    <!-- Final call to action -->
    <section class="section cta-band">
      <h2>Ready to try it?</h2>
      <p>Sign in with your account, or ask your admin for access.</p>
      <a href="/login" class="btn btn-primary">
        Go to sign in
        <ArrowRight size={18} />
      </a>
    </section>
  </main>

  <footer class="site-footer">
    <p>Meal Trackers · Frontend demo · API integration ready</p>
  </footer>
</div>

<style>
  .landing {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    background: var(--color-bg);
  }

  .top-nav {
    position: sticky;
    top: 0;
    z-index: 50;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 1.5rem;
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(8px);
    border-bottom: 1px solid var(--color-border);
  }

  .brand {
    display: flex;
    align-items: center;
    gap: 0.625rem;
    font-weight: 700;
    font-size: 1.0625rem;
    color: var(--color-primary);
    text-decoration: none;
  }

  .brand-mark {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    background: var(--color-accent);
    color: white;
    border-radius: var(--radius-md);
  }

  .nav-links {
    display: flex;
    align-items: center;
    gap: 1.25rem;
  }

  .nav-links a:not(.btn) {
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--color-text-muted);
    text-decoration: none;
  }

  .nav-links a:not(.btn):hover {
    color: var(--color-accent);
  }

  .nav-cta {
    padding: 0.5rem 1rem;
  }

  @media (max-width: 640px) {
    .nav-links a:not(.btn):not(.nav-cta) {
      display: none;
    }
  }

  .hero {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 3rem;
    align-items: center;
    max-width: 1100px;
    margin: 0 auto;
    padding: 4rem 1.5rem 3rem;
  }

  @media (max-width: 900px) {
    .hero {
      grid-template-columns: 1fr;
      padding-top: 2.5rem;
    }

    .hero-card {
      order: -1;
    }
  }

  .eyebrow {
    display: inline-block;
    font-size: 0.8125rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--color-accent);
    margin-bottom: 0.75rem;
  }

  .hero h1 {
    font-size: clamp(1.875rem, 4vw, 2.75rem);
    line-height: 1.15;
    margin-bottom: 1rem;
  }

  .lead {
    font-size: 1.0625rem;
    color: var(--color-text-muted);
    line-height: 1.7;
    margin-bottom: 1.75rem;
    max-width: 32rem;
  }

  .hero-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
  }

  .hero-card {
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    padding: 2rem;
    box-shadow: var(--shadow-lg);
    text-align: center;
  }

  .mock-qr {
    display: flex;
    justify-content: center;
    color: var(--color-primary);
    margin-bottom: 1rem;
    opacity: 0.85;
  }

  .mock-label {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--color-text-muted);
    margin-bottom: 1.25rem;
  }

  .mock-stats {
    list-style: none;
    text-align: left;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    font-size: 0.875rem;
    color: var(--color-text);
  }

  .mock-stats li {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: var(--color-success);
  }

  .section {
    max-width: 1100px;
    margin: 0 auto;
    padding: 3rem 1.5rem;
  }

  .section.alt {
    background: var(--color-surface);
    border-top: 1px solid var(--color-border);
    border-bottom: 1px solid var(--color-border);
    max-width: none;
  }

  .section.alt > * {
    max-width: 1100px;
    margin-left: auto;
    margin-right: auto;
  }

  .section-head {
    text-align: center;
    margin-bottom: 2rem;
  }

  .section-head h2 {
    font-size: 1.75rem;
    margin-bottom: 0.5rem;
  }

  .section-head p {
    color: var(--color-text-muted);
  }

  .feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 1.25rem;
  }

  .feature-card {
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    transition: box-shadow 0.2s ease, transform 0.2s ease;
  }

  .feature-card:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-2px);
  }

  .feature-icon {
    width: 44px;
    height: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--color-accent-muted);
    color: var(--color-accent);
    border-radius: var(--radius-md);
    margin-bottom: 1rem;
  }

  .feature-card h3 {
    font-size: 1.0625rem;
    margin-bottom: 0.5rem;
  }

  .feature-card p {
    font-size: 0.9375rem;
    color: var(--color-text-muted);
    line-height: 1.6;
  }

  .steps {
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
    max-width: 640px;
    margin: 0 auto;
  }

  .steps li {
    display: flex;
    gap: 1rem;
    align-items: flex-start;
  }

  .step-num {
    flex-shrink: 0;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--color-accent);
    color: white;
    font-weight: 700;
    font-size: 0.875rem;
    border-radius: 50%;
  }

  .steps p {
    color: var(--color-text-muted);
    line-height: 1.6;
    padding-top: 0.25rem;
  }

  .cta-band {
    text-align: center;
  }

  .cta-band h2 {
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
  }

  .cta-band p {
    color: var(--color-text-muted);
    margin-bottom: 1.25rem;
  }

  .site-footer {
    margin-top: auto;
    padding: 1.5rem;
    text-align: center;
    font-size: 0.8125rem;
    color: var(--color-text-muted);
    border-top: 1px solid var(--color-border);
  }
</style>
