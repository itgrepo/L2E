<script setup>
import { ref } from 'vue';
import AppNavbar from '../components/AppNavbar.vue';
import AppFooter from '../components/AppFooter.vue';

const form = ref({
  name: '',
  email: '',
  subject: '',
  message: ''
});

const faqs = [
  { q: 'How do I request access to restricted data?', a: 'You can apply for access by clicking the "Request Access" button on the dataset detail page. You will need to provide a justification for your research or project.' },
  { q: 'What are the API rate limits?', a: 'Standard API keys have a limit of 1,000 requests per hour. For higher limits, please contact our support team.' },
  { q: 'How can I contribute my own datasets?', a: 'Agencies can register as data providers through the "Provider Portal". Once registered, you can upload and manage your datasets.' }
];

const activeFaq = ref(null);
</script>

<template>
  <div class="contact-page">
    <section class="contact-hero">
      <div class="container">
        <h1>Contact Us</h1>
        <p>Have questions or need assistance? Our team is here to help.</p>
      </div>
    </section>
    
    <div class="container contact-main">
      <div class="contact-grid">
        <div class="contact-form-area">
          <div class="card">
            <h3>Send us a message</h3>
            <form @submit.prevent="console.log('Form submitted', form)">
              <div class="form-row">
                <div class="form-group">
                  <label>Full Name</label>
                  <input type="text" v-model="form.name" placeholder="John Doe">
                </div>
                <div class="form-group">
                  <label>Email Address</label>
                  <input type="email" v-model="form.email" placeholder="john@example.com">
                </div>
              </div>
              <div class="form-group">
                <label>Subject</label>
                <input type="text" v-model="form.subject" placeholder="How can we help?">
              </div>
              <div class="form-group">
                <label>Message</label>
                <textarea v-model="form.message" rows="5" placeholder="Tell us more about your inquiry..."></textarea>
              </div>
              <button type="submit" class="btn-primary">Send Message</button>
            </form>
          </div>
        </div>
        
        <aside class="contact-info">
          <div class="info-card">
            <h4>Office Address</h4>
            <p>123 Government Complex, Building B<br>Chaeng Watthana Rd, Bangkok 10210</p>
          </div>
          <div class="info-card">
            <h4>Direct Contact</h4>
            <p><strong>Email:</strong> support@l2e.go.th</p>
            <p><strong>Phone:</strong> +66 2 123 4567</p>
          </div>
          <div class="social-links">
            <a href="#" class="social-icon">FB</a>
            <a href="#" class="social-icon">TW</a>
            <a href="#" class="social-icon">LI</a>
          </div>
        </aside>
      </div>
      
      <section class="faq-section">
        <h2>Frequently Asked Questions</h2>
        <div class="faq-list">
          <div v-for="(faq, index) in faqs" :key="index" class="faq-item">
            <button class="faq-quest" @click="activeFaq = activeFaq === index ? null : index">
              {{ faq.q }}
              <span class="plus">{{ activeFaq === index ? '−' : '+' }}</span>
            </button>
            <div v-if="activeFaq === index" class="faq-ans">
              <p>{{ faq.a }}</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.contact-page {
  background: #f8fafc;
  min-height: 100vh;
}

.contact-hero {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  color: white;
  padding: 80px 0;
  text-align: center;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

.contact-hero h1 {
  font-size: 3rem;
  font-weight: 800;
  margin-bottom: 16px;
}

.contact-hero p {
  font-size: 1.25rem;
  color: #94a3b8;
}

.contact-main {
  margin-top: -60px;
  padding-bottom: 80px;
}

.contact-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 32px;
  margin-bottom: 80px;
}

.card {
  background: white;
  padding: 40px;
  border-radius: 24px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
}

.card h3 {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 32px;
  color: #1e293b;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.form-group {
  margin-bottom: 24px;
}

label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: #475569;
  margin-bottom: 8px;
}

input, textarea {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  font-size: 1rem;
  transition: all 0.2s;
}

input:focus, textarea:focus {
  outline: none;
  border-color: var(--mso-accent);
  box-shadow: 0 0 0 4px rgba(34, 197, 94, 0.1);
}

.btn-primary {
  background: var(--mso-accent);
  color: white;
  border: none;
  padding: 14px 28px;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-primary:hover {
  background: var(--primary);
}

.contact-info {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.info-card {
  background: white;
  padding: 24px;
  border-radius: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.info-card h4 {
  font-size: 1rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 12px;
}

.info-card p {
  color: #64748b;
  line-height: 1.6;
  font-size: 0.9375rem;
}

.social-links {
  display: flex;
  gap: 12px;
}

.social-icon {
  width: 44px;
  height: 44px;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  text-decoration: none;
  font-weight: 700;
  color: #1e293b;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.faq-section h2 {
  text-align: center;
  font-size: 2.25rem;
  font-weight: 800;
  margin-bottom: 48px;
}

.faq-list {
  max-width: 800px;
  margin: 0 auto;
}

.faq-item {
  background: white;
  border-radius: 16px;
  margin-bottom: 12px;
  overflow: hidden;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.faq-quest {
  width: 100%;
  text-align: left;
  padding: 24px;
  background: none;
  border: none;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e293b;
  cursor: pointer;
}

.faq-ans {
  padding: 0 24px 24px;
  color: #64748b;
  line-height: 1.6;
}

.plus {
  color: var(--mso-accent);
  font-size: 1.5rem;
}
</style>
