<template>
  <div class="hero-mockup">
    <div class="mockup-window glass-panel">
      <div class="mockup-header">
        <div class="dots">
          <span></span><span></span><span></span>
        </div>
        <div class="mockup-title">Data Portal Preview</div>
      </div>
      <div class="mockup-body">
        <div class="mockup-grid">
          <div class="mockup-card">
            <div class="icon-blob" style="background: #eef2ff; color: #6366f1;">❖</div>
            <h4>Dataset Catalog</h4>
            <p>ค้นหาและเข้าถึงข้อมูลเปิดภาครัฐ</p>
          </div>
          <div class="mockup-card">
            <div class="icon-blob" style="background: #fef3c7; color: #d97706;">⚡</div>
            <h4>API Gateway</h4>
            <p>เชื่อมต่อข้อมูลผ่าน RESTful API อย่างปลอดภัย</p>
          </div>
          <div class="mockup-card">
            <div class="icon-blob" style="background: #fdf2f8; color: var(--mso-accent);">📈</div>
            <h4>Analytics</h4>
            <p>วิเคราะห์ผลตอบสนองและข้อมูลเชิงลึก</p>
          </div>
          <div class="mockup-card">
            <div class="icon-blob" style="background: #fef2f2; color: #ef4444;">🛡️</div>
            <h4>Data Governance</h4>
            <p>จัดการสิทธิ์และกำหนดนโยบายข้อมูล</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.hero-mockup {
  position: relative;
  perspective: 1000px;
}

.mockup-window {
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.4);
  border-radius: var(--radius-xl);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transform: rotateY(-3deg) rotateX(2deg);
  transition: transform 0.5s ease;
}

.mockup-window:hover {
  transform: rotateY(0deg) rotateX(0deg);
}

.mockup-header {
  display: flex;
  align-items: center;
  padding: 1rem 1.5rem;
  background: rgba(255, 255, 255, 0.6);
  border-bottom: 1px solid rgba(255, 255, 255, 0.5);
}

.dots {
  display: flex;
  gap: 6px;
  margin-right: 15px;
}

.dots span {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: #e2e8f0;
}
.dots span:nth-child(1) { background-color: #fecaca; }
.dots span:nth-child(2) { background-color: #fdf6b2; }
.dots span:nth-child(3) { background-color: #fbcfe8; }

.mockup-title {
  font-size: 0.85rem;
  font-weight: 500;
  color: #94a3b8;
}

.mockup-body {
  padding: 2rem;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.7) 0%, rgba(248, 250, 252, 0.4) 100%);
}

.mockup-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.mockup-card {
  background: white;
  padding: 1.5rem;
  border-radius: var(--radius-lg);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease;
}

.mockup-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

.icon-blob {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
  font-size: 1.2rem;
}

.mockup-card h4 {
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.mockup-card p {
  font-size: 0.75rem;
  color: var(--text-muted);
  line-height: 1.5;
}

@media (max-width: 1024px) {
  .mockup-window { transform: none; }
}

@media (max-width: 768px) {
  .mockup-grid { grid-template-columns: 1fr; }
  .mockup-body { padding: 1.5rem; }
}
</style>
