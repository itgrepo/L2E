<script setup>
import { ref } from 'vue';
import apiClient from '../services/api';

import AppNavbar from '../components/AppNavbar.vue';
import AppFooter from '../components/AppFooter.vue';

const form = ref({
  name: '',
  email: '',
  subject: '',
  message: ''
});

const faqs = [
  { q: 'ฉันจะขอเข้าถึงข้อมูลที่ถูกจำกัดได้อย่างไร?', a: 'คุณสามารถสมัครขอเข้าถึงข้อมูลได้โดยคลิกปุ่ม "ขอสิทธิ์เข้าถึง" ในหน้ารายละเอียดชุดข้อมูล โดยคุณต้องระบุเหตุผลในการวิจัยหรือโครงการของคุณ' },
  { q: 'ข้อจำกัดในการเรียกใช้ API คืออะไร?', a: 'คีย์ API มาตรฐานมีข้อจำกัดในการเรียกใช้งาน 1,000 ครั้งต่อชั่วโมง หากต้องการขยายขีดจำกัด โปรดติดต่อทีมสนับสนุนของเรา' },
  { q: 'ฉันจะนำชุดข้อมูลของตัวเองมาเผยแพร่ได้อย่างไร?', a: 'หน่วยงานสามารถลงทะเบียนเป็นผู้ให้บริการข้อมูลผ่าน "พอร์ทัลผู้ให้บริการ" เมื่อลงทะเบียนแล้ว คุณสามารถอัปโหลดและจัดการชุดข้อมูลของคุณได้' }
];

const activeFaq = ref(null);

const isSubmitting = ref(false);

const submitContact = async () => {
  if (isSubmitting.value) return;
  isSubmitting.value = true;
  
  try {
    const res = await apiClient.post('/submitContact', form.value);
    if (res.data.status === 'success') {
      alert('ส่งข้อความสำเร็จ! ทางเราได้รับข้อความของคุณเรียบร้อยแล้ว');
      form.value = { name: '', email: '', subject: '', message: '' };
    } else {
      alert('เกิดข้อผิดพลาดในการส่งข้อความ: ' + res.data.message);
    }
  } catch (error) {
    console.error(error);
    alert('ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้ กรุณาลองใหม่อีกครั้ง');
  } finally {
    isSubmitting.value = false;
  }
};

</script>

<template>
  <div class="contact-page">
    <section class="contact-hero">
      <div class="container">
        <h1>ติดต่อเรา</h1>
        <p>มีคำถามหรือต้องการความช่วยเหลือ? ทีมงานของเราพร้อมให้บริการ</p>
      </div>
    </section>
    
    <div class="container contact-main">
      <div class="contact-grid">
        <div class="contact-form-area">
          <div class="card">
            <h3>ส่งข้อความถึงเรา</h3>
            <form @submit.prevent="submitContact">
              <div class="form-row">
                <div class="form-group">
                  <label>ชื่อ-นามสกุล</label>
                  <input type="text" v-model="form.name" placeholder="สมชาย ใจดี" required maxlength="100">
                </div>
                <div class="form-group">
                  <label>อีเมล</label>
                  <input type="email" v-model="form.email" placeholder="somchai@example.com" required maxlength="100">
                </div>
              </div>
              <div class="form-group">
                <label>หัวข้อ</label>
                <input type="text" v-model="form.subject" placeholder="ให้เราช่วยเหลือเรื่องใด?">
              </div>
              <div class="form-group">
                <label>ข้อความ</label>
                <textarea v-model="form.message" rows="5" placeholder="บอกรายละเอียดเพิ่มเติมเกี่ยวกับการสอบถามของคุณ..." required maxlength="1000"></textarea>
              </div>
              <button type="submit" class="btn-primary" :disabled="isSubmitting">{{ isSubmitting ? "กำลังส่ง..." : "Send ข้อความ" }}</button>
            </form>
          </div>
        </div>
        
        <aside class="contact-info">
          <div class="info-card">
            <h4>ที่อยู่สำนักงาน</h4>
            <p>สำนักงานคณะกรรมการดิจิทัลเพื่อเศรษฐกิจและสังคมแห่งชาติ (สดช.)<br>เลขที่ 120 หมู่ 3 ชั้น 3 และ 5 ศูนย์ราชการฯ แจ้งวัฒนะ (อาคาร ซี)<br>ซอยแจ้งวัฒนะ 7 ถนนแจ้งวัฒนะ แขวงทุ่งสองห้อง เขตหลักสี่ กรุงเทพฯ 10210</p>
          </div>
          <div class="info-card">
            <h4>ข้อมูลติดต่อโดยตรง</h4>
            <p><strong><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="display:inline; vertical-align:text-bottom; margin-right:4px;"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg> Email:</strong> learn2earn@bde.go.th</p>
            <p><strong><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="display:inline; vertical-align:text-bottom; margin-right:4px;"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" /></svg> Phone:</strong> 02-079-1389</p>
          </div>
          <div class="social-links" style="display: none;">
            <a href="#" class="social-icon">FB</a>
            <a href="#" class="social-icon">TW</a>
            <a href="#" class="social-icon">LI</a>
          </div>
        </aside>
      </div>
      
      <section class="faq-section" style="display: none;">
        <h2>คำถามที่พบบ่อย</h2>
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
