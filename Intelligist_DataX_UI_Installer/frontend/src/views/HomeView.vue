<script setup>
import { computed } from 'vue';
import { pageLayout } from '../utils/pageBuilder';
import HeroSection from '../components/HeroSection.vue';
import FeatureSection from '../components/FeatureSection.vue';
import StepSection from '../components/StepSection.vue';
import StatsBanner from '../components/StatsBanner.vue';
import CTASection from '../components/CTASection.vue';
import PageBuilderWidget from '../components/PageBuilderWidget.vue';

// Map component names to actual components
const componentsMap = {
  HeroSection,
  FeatureSection,
  StepSection,
  StatsBanner,
  CTASection
};

const getComponent = (type) => componentsMap[type];
</script>

<template>
  <div class="home-view">
    <template v-for="block in pageLayout" :key="block.id">
      <component 
        v-if="block.visible"
        :is="getComponent(block.type)" 
        :config="block.props" 
      />
    </template>
    
    <PageBuilderWidget />
  </div>
</template>

<style scoped>
.home-view {
  width: 100%;
}
</style>
