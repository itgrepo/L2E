<script setup>
import { onMounted } from 'vue';
import { RouterView } from 'vue-router';
import AppNavbar from './components/AppNavbar.vue';
import AppFooter from './components/AppFooter.vue';
import ThemeWidget from './components/ThemeWidget.vue';
import { applyTheme, loadThemeFromServer } from './utils/theme';
import { loadLayoutFromServer } from './utils/pageBuilder';

onMounted(() => {
  applyTheme();
  loadThemeFromServer();
  loadLayoutFromServer();
});
</script>

<template>
  <div class="app-layout">
    <AppNavbar />
    
    <main>
      <router-view v-slot="{ Component }">
        <keep-alive>
          <component :is="Component" />
        </keep-alive>
      </router-view>
    </main>

    <AppFooter />
    <ThemeWidget />
  </div>
</template>

<style scoped>
.app-layout {
  min-height: 100dvh;
  display: flex;
  flex-direction: column;
}

main {
  flex: 1;
}

/* Padding to prevent content from going under fixed navbar on mobile */
@media (max-width: 768px) {
  .app-layout {
    padding-top: 70px;
  }
}
</style>
