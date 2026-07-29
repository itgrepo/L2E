<script setup>
import AppNavbar from '../components/AppNavbar.vue';
import AppFooter from '../components/AppFooter.vue';
</script>

<template>
  <div class="about-page">
    <section class="about-hero">
      <div class="container">
        <h1>About Intelligist DataX Portal</h1>
        <p class="subtitle">The central hub for MSDHS data exchange and API management.</p>
      </div>
    </section>
    
    <section class="mission-section">
      <div class="container grid">
        <div class="mission-content">
          <h2>Our Mission</h2>
          <p>Intelligist DataX Portal (MSDHS Data Exchange & API Management Platform) is designed to streamline the way government agencies share, discover, and utilize data. Our mission is to create a seamless, secure, and standardized ecosystem that empowers developers and policy-makers with high-quality data.</p>
          <div class="stats-mini">
            <div class="stat">
              <span class="num">50+</span>
              <span class="lbl">Agencies</span>
            </div>
            <div class="stat">
              <span class="num">2,000+</span>
              <span class="lbl">Datasets</span>
            </div>
            <div class="stat">
              <span class="num">10M+</span>
              <span class="lbl">API Calls</span>
            </div>
          </div>
        </div>
        <div class="mission-image">
          <div class="abstract-shape">
            <div class="circle c1"></div>
            <div class="circle c2"></div>
            <div class="logo-placeholder">Intelligist DataX</div>
          </div>
        </div>
      </div>
    </section>
    
    <section class="features-grid-section">
      <div class="container">
        <h2 class="text-center">How it works</h2>
        <div class="features-grid">
          <div class="feature-item">
            <div class="icon-box">🔍</div>
            <h3>Discover</h3>
            <p>Easily find the data you need through our powerful search and smart categorization system.</p>
          </div>
          <div class="feature-item">
            <div class="icon-box">🔌</div>
            <h3>Connect</h3>
            <p>Get instant access via standardized APIs with complete documentation and code samples.</p>
          </div>
          <div class="feature-item">
            <div class="icon-box">🛡️</div>
            <h3>Secure</h3>
            <p>Industry-standard authentication and auditing ensure that data is only accessed by authorized parties.</p>
          </div>
          <div class="feature-item">
            <div class="icon-box">📊</div>
            <h3>Analyze</h3>
            <p>Monitor your data usage and gain insights through comprehensive analytics dashboards.</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.about-page {
  background: white;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

.about-hero {
  background: #f8fafc;
  padding: 120px 0;
  text-align: center;
}

.about-hero h1 {
  font-size: 3.5rem;
  font-weight: 800;
  color: #1e293b;
  margin-bottom: 16px;
}

.subtitle {
  font-size: 1.5rem;
  color: #64748b;
  max-width: 700px;
  margin: 0 auto;
}

.mission-section {
  padding: 100px 0;
}

.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  align-items: center;
  gap: 80px;
}

h2 {
  font-size: 2.5rem;
  font-weight: 800;
  color: #1e293b;
  margin-bottom: 24px;
}

.mission-content p {
  font-size: 1.125rem;
  line-height: 1.8;
  color: #475569;
  margin-bottom: 40px;
}

.stats-mini {
  display: flex;
  gap: 40px;
}

.stat {
  display: flex;
  flex-direction: column;
}

.num {
  font-size: 2rem;
  font-weight: 800;
  color: var(--primary);
}

.lbl {
  color: #94a3b8;
  font-weight: 600;
}

.abstract-shape {
  position: relative;
  width: 400px;
  height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.circle {
  position: absolute;
  border-radius: 50%;
}

.c1 {
  width: 100%;
  height: 100%;
  background: #fdf2f8;
  animation: pulse 4s infinite;
}

.c2 {
  width: 70%;
  height: 70%;
  background: #fce7f3;
  animation: pulse 3s infinite reverse;
}

.logo-placeholder {
  position: relative;
  z-index: 2;
  font-size: 3rem;
  font-weight: 800;
  color: var(--primary);
}

@keyframes pulse {
  0% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.1); opacity: 0.8; }
  100% { transform: scale(1); opacity: 0.5; }
}

.features-grid-section {
  padding: 100px 0;
  background: #f8fafc;
}

.text-center { text-align: center; margin-bottom: 60px; }

.features-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 32px;
}

.feature-item {
  background: white;
  padding: 40px;
  border-radius: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.icon-box {
  font-size: 2.5rem;
  margin-bottom: 24px;
}

.feature-item h3 {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 16px;
  color: #1e293b;
}

.feature-item p {
  line-height: 1.6;
  color: #64748b;
}
</style>
