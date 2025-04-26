<template>
  <div class="landing-page">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-particles" ref="particlesContainer"></div>

      <div class="hero-content" :class="{ 'fade-out': showSidebar }">
        <h1 class="hero-title">
          <span class="gradient-text">Cool Master</span><br />
          設計平台
        </h1>
        <h2 class="hero-subtitle">
          使用AI驅動的工具和市場洞察創建尖端庫瑪設計
        </h2>
        <div class="hero-actions">
          <n-button
            type="primary"
            size="large"
            class="get-started-btn"
            @click="handleGetStarted"
          >
            開始設計
            <template #icon
              ><n-icon><ArrowRightIcon /></n-icon
            ></template>
          </n-button>
          <n-button
            quaternary
            size="large"
            class="learn-more-btn"
            @click="scrollToFeatures"
          >
            了解更多
            <template #icon
              ><n-icon><ChevronDownIcon /></n-icon
            ></template>
          </n-button>
        </div>
      </div>

      <div class="floating-images">
        <div
          v-for="(img, i) in floatingImages"
          :key="i"
          class="floating-image"
          :style="{
            backgroundImage: `url(${img.url})`,
            animationDelay: `${i * 0.5}s`,
            top: `${img.top}%`,
            left: `${img.left}%`,
            width: `${img.size}px`,
            height: `${img.size}px`,
            zIndex: img.zIndex,
          }"
        ></div>
      </div>
    </section>

    <!-- Features Grid Section -->
    <section class="features-section" id="features">
      <div class="section-header">
        <h2 class="section-title">革命性設計功能</h2>
        <p class="section-subtitle">透過我們的AI驅動設計工具釋放您的創造力</p>
      </div>

      <div class="features-grid">
        <div
          v-for="(feature, index) in features"
          :key="index"
          class="feature-card"
          :class="{ 'feature-highlight': index === 0 || index === 3 }"
          @mouseenter="featureHovered = index"
          @mouseleave="featureHovered = null"
        >
          <div class="feature-icon">
            <n-icon :size="32" :color="feature.color">
              <component :is="feature.icon" />
            </n-icon>
          </div>
          <h3 class="feature-title">{{ feature.title }}</h3>
          <p class="feature-desc">{{ feature.description }}</p>
        </div>
      </div>
    </section>

    <!-- Design Process Section -->
    <section class="process-section">
      <div class="section-header">
        <h2 class="section-title">精簡設計流程</h2>
        <p class="section-subtitle">從概念到完成只需幾分鐘，而非數天</p>
      </div>

      <div class="process-steps">
        <div
          class="process-step"
          v-for="(step, index) in designSteps"
          :key="index"
        >
          <div class="step-number">{{ index + 1 }}</div>
          <div class="step-content">
            <h3>{{ step.title }}</h3>
            <p>{{ step.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Showcase Section -->
    <section class="showcase-section">
      <div class="section-header">
        <h2 class="section-title">平台上創建的精美設計</h2>
        <p class="section-subtitle">加入全球數千名設計師的行列</p>
      </div>
    </section>

    <!-- Testimonials Section -->
    <section class="testimonials-section">
      <div class="section-header">
        <h2 class="section-title">設計師怎麼說</h2>
        <p class="section-subtitle">加入我們不斷成長的創作者社區</p>
      </div>

      <div class="testimonials-slider" ref="testimonialsSlider">
        <div
          class="testimonial-card"
          v-for="(testimonial, index) in testimonials"
          :key="index"
        >
          <div class="testimonial-content">
            <div class="quote-icon">"</div>
            <p class="testimonial-text">{{ testimonial.text }}</p>
            <div class="testimonial-author">
              <div
                class="author-avatar"
                :style="{ backgroundImage: `url(${testimonial.avatar})` }"
              ></div>
              <div class="author-info">
                <h4>{{ testimonial.name }}</h4>
                <p>{{ testimonial.role }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Call to Action Section -->
    <section class="cta-section">
      <div class="cta-content">
        <h2 class="cta-title">準備好革新您的庫瑪設計了嗎？</h2>
        <p class="cta-subtitle">加入使用AI驅動工具創建下一位庫瑪設計師行列</p>
        <n-button
          type="primary"
          size="large"
          class="cta-button"
          @click="handleGetStarted"
        >
          立即開始設計
          <template #icon
            ><n-icon><ArrowRightIcon /></n-icon
          ></template>
        </n-button>
      </div>

      <div class="cta-background"></div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, h } from "vue";
import { useRouter } from "vue-router";
import { NButton, NIcon } from "naive-ui";
import gsap from "gsap";
import { useI18n } from "vue-i18n";

const { t } = useI18n();

// Icons
const ArrowRightIcon = () =>
  h(
    "svg",
    {
      xmlns: "http://www.w3.org/2000/svg",
      viewBox: "0 0 24 24",
      fill: "none",
      stroke: "currentColor",
      "stroke-width": "2",
      "stroke-linecap": "round",
      "stroke-linejoin": "round",
    },
    [
      h("line", { x1: "5", y1: "12", x2: "19", y2: "12" }),
      h("polyline", { points: "12 5 19 12 12 19" }),
    ]
  );

const ChevronDownIcon = () =>
  h(
    "svg",
    {
      xmlns: "http://www.w3.org/2000/svg",
      viewBox: "0 0 24 24",
      fill: "none",
      stroke: "currentColor",
      "stroke-width": "2",
      "stroke-linecap": "round",
      "stroke-linejoin": "round",
    },
    [h("polyline", { points: "6 9 12 15 18 9" })]
  );

const BrushIcon = () =>
  h(
    "svg",
    {
      xmlns: "http://www.w3.org/2000/svg",
      viewBox: "0 0 24 24",
      fill: "none",
      stroke: "currentColor",
      "stroke-width": "2",
      "stroke-linecap": "round",
      "stroke-linejoin": "round",
    },
    [
      h("path", {
        d: "M9.06 11.9c-1.06 1.06-1.44 2.67-.9 4.07 1.97-1.97 3.03-3.03 3.03-4.24 0-.7-.57-1.27-1.27-1.27-.28 0-.53.09-.76.26l-.1.08z",
      }),
      h("path", {
        d: "M8 21s-.84-3.58 2.23-5.23c.86-.46 1.77.2 1.77 1.16 0 1.5-1.5 1.77-3.24 3.69l-.76.38z",
      }),
      h("path", {
        d: "M17.97 12.97 19 14l1.9-1.9c.37-.37.37-.97 0-1.34L15.07 5.07a.95.95 0 0 0-1.34 0L12 6.81M9.06 9.06 3.07 15.07c-.37.37-.37.97 0 1.34L4.1 17.1",
      }),
    ]
  );

const SparklesIcon = () =>
  h(
    "svg",
    {
      xmlns: "http://www.w3.org/2000/svg",
      viewBox: "0 0 24 24",
      fill: "none",
      stroke: "currentColor",
      "stroke-width": "2",
      "stroke-linecap": "round",
      "stroke-linejoin": "round",
    },
    [
      h("path", { d: "M12 3v5m0 0v5m0-5H7m5 0h5" }),
      h("path", { d: "M5 13v5m0 0v3m0-3H2m3 0h3" }),
      h("path", { d: "M19 13v3m0 0v5m0-5h-3m3 0h3" }),
    ]
  );

const RocketIcon = () =>
  h(
    "svg",
    {
      xmlns: "http://www.w3.org/2000/svg",
      viewBox: "0 0 24 24",
      fill: "none",
      stroke: "currentColor",
      "stroke-width": "2",
      "stroke-linecap": "round",
      "stroke-linejoin": "round",
    },
    [
      h("path", {
        d: "M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z",
      }),
      h("path", {
        d: "m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z",
      }),
      h("path", { d: "m9 12 3 3" }),
    ]
  );

const LayersIcon = () =>
  h(
    "svg",
    {
      xmlns: "http://www.w3.org/2000/svg",
      viewBox: "0 0 24 24",
      fill: "none",
      stroke: "currentColor",
      "stroke-width": "2",
      "stroke-linecap": "round",
      "stroke-linejoin": "round",
    },
    [
      h("polygon", { points: "12 2 2 7 12 12 22 7 12 2" }),
      h("polyline", { points: "2 17 12 22 22 17" }),
      h("polyline", { points: "2 12 12 17 22 12" }),
    ]
  );

const LightningIcon = () =>
  h(
    "svg",
    {
      xmlns: "http://www.w3.org/2000/svg",
      viewBox: "0 0 24 24",
      fill: "none",
      stroke: "currentColor",
      "stroke-width": "2",
      "stroke-linecap": "round",
      "stroke-linejoin": "round",
    },
    [h("path", { d: "M13 2 3 14h9l-1 8 10-12h-9l1-8z" })]
  );

// State
const router = useRouter();
const showSidebar = ref(false);
const particlesContainer = ref(null);
const featureHovered = ref(null);
const testimonialsSlider = ref(null);

// PC case images for floating animation
// const floatingImages = ref([
//   {
//     url: new URL("../assets/homepage_img/1.png", import.meta.url).href,
//     top: 10,
//     left: 80,
//     size: 200,
//     zIndex: 2,
//   },
//   {
//     url: new URL("../assets/homepage_img/2.png", import.meta.url).href,
//     top: 60,
//     left: 75,
//     size: 150,
//     zIndex: 1,
//   },
//   {
//     url: new URL("../assets/homepage_img/3.png", import.meta.url).href,
//     top: 30,
//     left: 83,
//     size: 180,
//     zIndex: 3,
//   },
//   {
//     url: new URL("../assets/homepage_img/4.png", import.meta.url).href,
//     top: 70,
//     left: 15,
//     size: 230,
//     zIndex: 1,
//   },
//   {
//     url: new URL("../assets/homepage_img/5.png", import.meta.url).href,
//     top: 20,
//     left: 10,
//     size: 170,
//     zIndex: 2,
//   },
// ]);

// Features grid data
const features = [
  {
    icon: RocketIcon,
    color: "#6366f1",
    title: "AI 驅動設計生成",
    description:
      "利用 Stability AI、Titan ImageGenerator G1 和 Nova Canvas 等多種 AI 模型，轉化您的電腦機殼概念。",
  },
  {
    icon: BrushIcon,
    color: "#ec4899",
    title: "圖像局部重繪與客製化",
    description:
      "運用我們先進的局部重繪 (inpainting) 技術重現部分設計 - 修改特定細節，同時保留您的核心設計元素。",
  },
  {
    icon: LayersIcon,
    color: "#f97316",
    title: "市場趨勢整合",
    description:
      "從我們的網路爬蟲系統獲取即時的設計洞察，該系統分析來自主要零售商的當前市場趨勢。",
  },
  {
    icon: SparklesIcon,
    color: "#0ea5e9",
    title: "參數化設計控制",
    description:
      "透過對顏色、材質、尺寸和其他關鍵設計元素的精確參數控制來微調您的設計。",
  },
  {
    icon: LightningIcon,
    color: "#8b5cf6",
    title: "專案模板與歷史紀錄",
    description:
      "將設計另存為模板，瀏覽您的設計歷史紀錄，並透過標籤或風格篩選專案以便快速參考。",
  },
  {
    icon: ChevronDownIcon,
    color: "#10b981",
    title: "進階圖像處理",
    description:
      "使用 Nova Canvas 工具手動修改圖像，或上傳您自己的藍圖以進行 AI 強化和整合。",
  },
];

// Design Process steps
const designSteps = computed(() => [
  {
    title: t("designInputTitle"),
    description: t("designInputDescription"),
  },
  {
    title: t("aiGenerateTitle"),
    description: t("aiGenerateDescription"),
  },
  {
    title: t("designerRevisionTitle"),
    description: t("designerRevisionDescription"),
  },
  {
    title: t("integrationTitle"),
    description: t("integrationDescription"),
  },
]);
const galleryItems = ref([
  {
    image: new URL("../assets/homepage_img/1.png", import.meta.url).href,
    title: "Futuristic PC Case Design",
    description: "Generated with Stability AI model",
  },
  {
    image: new URL("../assets/homepage_img/2.png", import.meta.url).href,
    title: "RGB Gaming Tower",
    description: "Created using Nova Canvas tools",
  },
  {
    image: new URL("../assets/homepage_img/3.png", import.meta.url).href,
    title: "Minimalist Workstation Case",
    description: "Design with custom inpainting",
  },
  {
    image: new URL("../assets/homepage_img/4.png", import.meta.url).href,
    title: "Custom PC Case Design",
    description: "User-enhanced with partial regeneration",
  },
  {
    image: new URL("../assets/homepage_img/5.png", import.meta.url).href,
    title: "Compact Mini ITX Case",
    description: "Space-efficient design with glass panel",
  },
  {
    image: new URL("../assets/homepage_img/6.png", import.meta.url).href,
    title: "High Airflow Gaming Case",
    description: "Performance-optimized with metal accents",
  },
  {
    image: new URL("../assets/homepage_img/7.png", import.meta.url).href,
    title: "Water-Cooled Build Concept",
    description: "Design with integrated cooling support",
  },
  {
    image: new URL("../assets/homepage_img/8.png", import.meta.url).href,
    title: "Modern Tower PC Case",
    description: "Created with market trend data from Amazon",
  },
  {
    image: new URL("../assets/homepage_img/9.png", import.meta.url).href,
    title: "Portable SFF Gaming Case",
    description: "Designed with Titan Image Generator",
  },
]);

// Testimonials
const testimonials = [
  {
    text: "Cool Master 設計平台徹底改變了我們的電腦機殼設計工作流程。AI 基於市場趨勢生成概念的能力，為我們節省了數週的研究和原型製作時間。",
    name: "Alex Chen",
    role: "CaseLabs 產品設計師",
    avatar: "https://randomuser.me/api/portraits/men/32.jpg",
  },
  {
    text: "局部重繪 (inpainting) 功能對於優化特定機殼元素來說真是太棒了。我可以專注於完善側板和前面板等細節，同時保留整體的設計語言。",
    name: "Sarah Johnson",
    role: "獨立電腦改裝玩家",
    avatar: "https://randomuser.me/api/portraits/women/44.jpg",
  },
  {
    text: "能夠從主要零售商抓取設計數據並將其與 AI 生成整合，幫助我們創造出完美平衡創新與市場需求的機殼。",
    name: "Michael Rodriguez",
    role: "NextGen Computing 設計主管",
    avatar: "https://randomuser.me/api/portraits/men/67.jpg",
  },
  {
    text: "材質和尺寸的參數控制讓我能夠快速嘗試不同的製造可能性，更容易設計出既美觀又易於生產的機殼。",
    name: "Emma Wilson",
    role: "工業設計師",
    avatar: "https://randomuser.me/api/portraits/women/23.jpg",
  },
];

// Methods
const handleGetStarted = () => {
  showSidebar.value = true;

  // Animate sidebar sliding in
  const appLayout = document.querySelector(".app-layout");
  if (appLayout) {
    appLayout.classList.remove("sidebar-collapsed");
  }

  // Navigate to the first step in the workflow
  setTimeout(() => {
    router.push("/project");
  }, 300);
};

const scrollToFeatures = () => {
  document.getElementById("features").scrollIntoView({
    behavior: "smooth",
  });
};

// Animations and effects
onMounted(() => {
  // Initialize particles
  if (particlesContainer.value) {
    initParticles();
  }

  // Animate hero section elements
  gsap.from(".hero-title", {
    duration: 1,
    y: 50,
    opacity: 0,
    ease: "power3.out",
  });

  gsap.from(".hero-subtitle", {
    duration: 1,
    y: 30,
    opacity: 0,
    ease: "power3.out",
    delay: 0.3,
  });

  gsap.from(".hero-actions", {
    duration: 1,
    y: 20,
    opacity: 0,
    ease: "power3.out",
    delay: 0.6,
  });

  // Animate floating images
  gsap.from(".floating-image", {
    duration: 1.5,
    scale: 0.5,
    opacity: 0,
    stagger: 0.2,
    ease: "back.out(1.7)",
    delay: 0.5,
  });

  // Initialize testimonials slider
  initTestimonialsSlider();

  // Start feature card animations
  initFeatureAnimations();
});

const initParticles = () => {
  const particles = [];
  const canvas = document.createElement("canvas");
  const ctx = canvas.getContext("2d");

  particlesContainer.value.appendChild(canvas);

  const resizeCanvas = () => {
    if (particlesContainer.value) {
      canvas.width = particlesContainer.value.clientWidth;
      canvas.height = particlesContainer.value.clientHeight;
    }
  };

  resizeCanvas();
  window.addEventListener("resize", resizeCanvas);

  // Create particles
  for (let i = 0; i < 100; i++) {
    particles.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      radius: Math.random() * 2 + 1,
      speedX: Math.random() * 0.5 - 0.25,
      speedY: Math.random() * 0.5 - 0.25,
      opacity: Math.random() * 0.5 + 0.5,
    });
  }

  // Animation loop
  const animate = () => {
    requestAnimationFrame(animate);
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    particles.forEach((particle) => {
      // Update position
      particle.x += particle.speedX;
      particle.y += particle.speedY;

      // Wrap around edges
      if (particle.x < 0) particle.x = canvas.width;
      if (particle.x > canvas.width) particle.x = 0;
      if (particle.y < 0) particle.y = canvas.height;
      if (particle.y > canvas.height) particle.y = 0;

      // Draw particle
      ctx.beginPath();
      ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(255, 255, 255, ${particle.opacity})`;
      ctx.fill();
    });
  };

  animate();
};

const initTestimonialsSlider = () => {
  if (!testimonialsSlider.value) return;

  let isDown = false;
  let startX;
  let scrollLeft;

  testimonialsSlider.value.addEventListener("mousedown", (e) => {
    isDown = true;
    startX = e.pageX - testimonialsSlider.value.offsetLeft;
    scrollLeft = testimonialsSlider.value.scrollLeft;
  });

  testimonialsSlider.value.addEventListener("mouseleave", () => {
    isDown = false;
  });

  testimonialsSlider.value.addEventListener("mouseup", () => {
    isDown = false;
  });

  testimonialsSlider.value.addEventListener("mousemove", (e) => {
    if (!isDown) return;
    e.preventDefault();
    const x = e.pageX - testimonialsSlider.value.offsetLeft;
    const walk = (x - startX) * 2;
    testimonialsSlider.value.scrollLeft = scrollLeft - walk;
  });

  // Auto scroll
  const autoScroll = setInterval(() => {
    if (testimonialsSlider.value) {
      testimonialsSlider.value.scrollLeft += 1;

      // Reset scroll when reaching the end
      if (
        testimonialsSlider.value.scrollLeft >=
        testimonialsSlider.value.scrollWidth -
          testimonialsSlider.value.clientWidth
      ) {
        testimonialsSlider.value.scrollLeft = 0;
      }
    }
  }, 30);

  onUnmounted(() => {
    clearInterval(autoScroll);
  });
};

const initFeatureAnimations = () => {
  const featureCards = document.querySelectorAll(".feature-card");

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry, index) => {
        if (entry.isIntersecting) {
          gsap.to(entry.target, {
            y: 0,
            opacity: 1,
            duration: 0.6,
            delay: index * 0.1,
            ease: "power2.out",
          });
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.2 }
  );

  featureCards.forEach((card) => {
    gsap.set(card, { y: 50, opacity: 0 });
    observer.observe(card);
  });
};
</script>

<style scoped>
.landing-page {
  overflow-x: hidden;
}

/* Hero Section */
.hero-section {
  height: 100vh;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
  overflow: hidden;
}

.hero-particles {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.hero-content {
  max-width: 800px;
  text-align: center;
  padding: 2rem;
  position: relative;
  z-index: 10;
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.hero-content.fade-out {
  opacity: 0.3;
  transform: scale(0.95);
}

.hero-title {
  font-size: 4rem;
  font-weight: 800;
  line-height: 1.2;
  margin-bottom: 1.5rem;
  color: white;
}

.gradient-text {
  background: linear-gradient(90deg, #6366f1, #ec4899, #f97316);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  text-fill-color: transparent;
}

.hero-subtitle {
  font-size: 1.5rem;
  font-weight: 400;
  margin-bottom: 3rem;
  color: rgba(255, 255, 255, 0.8);
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.hero-actions {
  display: flex;
  gap: 1.5rem;
  justify-content: center;
}

.get-started-btn {
  font-weight: 600;
  padding: 0 2rem;
  height: 50px;
  font-size: 1.1rem;
  border-radius: 9999px;
  background: linear-gradient(90deg, #6366f1, #ec4899);
  box-shadow: 0 10px 15px -3px rgba(99, 102, 241, 0.3);
  transition: transform 0.2s, box-shadow 0.2s;
}

.get-started-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 15px 30px -5px rgba(99, 102, 241, 0.4);
}

.learn-more-btn {
  font-weight: 500;
  color: white;
  height: 50px;
  font-size: 1.1rem;
}

/* Floating Images Animation */
.floating-images {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 2;
  pointer-events: none;
}

.floating-image {
  position: absolute;
  background-size: cover;
  background-position: center;
  border-radius: 12px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3),
    0 10px 10px -5px rgba(0, 0, 0, 0.2);
  animation: float 8s ease-in-out infinite;
}

@keyframes float {
  0% {
    transform: translate(0, 0) rotate(0deg);
  }
  25% {
    transform: translate(10px, -15px) rotate(2deg);
  }
  50% {
    transform: translate(5px, 10px) rotate(-1deg);
  }
  75% {
    transform: translate(-10px, 15px) rotate(1deg);
  }
  100% {
    transform: translate(0, 0) rotate(0deg);
  }
}

/* Features Section */
.features-section {
  padding: 6rem 2rem;
  background: white;
}

.section-header {
  text-align: center;
  max-width: 700px;
  margin: 0 auto 4rem;
}

.section-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
  color: #1e293b;
}

.section-subtitle {
  font-size: 1.25rem;
  color: #64748b;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.feature-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1),
    0 4px 6px -2px rgba(0, 0, 0, 0.05);
  padding: 2rem;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  position: relative;
  overflow: hidden;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1),
    0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.feature-card::after {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 6px;
  height: 100%;
  background: linear-gradient(to bottom, #6366f1, #ec4899);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.feature-card:hover::after {
  opacity: 1;
}

.feature-icon {
  background: #f8fafc;
  width: 64px;
  height: 64px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.5rem;
}

.feature-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
  color: #1e293b;
}

.feature-desc {
  color: #64748b;
  line-height: 1.7;
}

.feature-highlight {
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
}

/* Design Process Section */
.process-section {
  padding: 6rem 2rem;
  background: #f8fafc;
}

.process-steps {
  max-width: 900px;
  margin: 0 auto;
  position: relative;
}

.process-steps::before {
  content: "";
  position: absolute;
  top: 0;
  left: 30px;
  height: 100%;
  width: 2px;
  background: #e2e8f0;
}

.process-step {
  display: flex;
  align-items: flex-start;
  margin-bottom: 3rem;
  position: relative;
}

.process-step:last-child {
  margin-bottom: 0;
}

.step-number {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  font-size: 1.5rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 2rem;
  box-shadow: 0 10px 15px -3px rgba(139, 92, 246, 0.3);
  z-index: 1;
}

.step-content {
  flex: 1;
  padding-top: 0.5rem;
}

.step-content h3 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
  color: #1e293b;
}

.step-content p {
  color: #64748b;
  line-height: 1.7;
  font-size: 1.1rem;
}

/* Showcase Section */
.showcase-section {
  padding: 6rem 2rem;
  background: white;
}

.showcase-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
  max-width: 1200px;
  margin: 0 auto;
}

.gallery-item {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

.gallery-image {
  height: 300px;
  background-size: cover;
  background-position: center;
  position: relative;
  transition: transform 0.5s ease;
}

.gallery-item:hover .gallery-image {
  transform: scale(1.05);
}

.gallery-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  padding: 1.5rem;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.8), transparent);
  color: white;
  transform: translateY(100%);
  transition: transform 0.3s ease;
}

.gallery-item:hover .gallery-overlay {
  transform: translateY(0);
}

.gallery-overlay h4 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.gallery-overlay p {
  font-size: 0.875rem;
  opacity: 0.8;
}

/* Testimonials Section */
.testimonials-section {
  padding: 6rem 2rem;
  background: #f8fafc;
}

.testimonials-slider {
  display: flex;
  gap: 2rem;
  padding: 1rem;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  scroll-behavior: smooth;
  -ms-overflow-style: none;
  scrollbar-width: none;
}

.testimonials-slider::-webkit-scrollbar {
  display: none;
}

.testimonial-card {
  min-width: 350px;
  max-width: 350px;
  scroll-snap-align: start;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.testimonial-content {
  position: relative;
}

.quote-icon {
  position: absolute;
  top: -15px;
  left: -10px;
  font-size: 4rem;
  font-family: serif;
  color: rgba(99, 102, 241, 0.1);
}

.testimonial-text {
  font-style: italic;
  line-height: 1.8;
  color: #475569;
  margin-bottom: 1.5rem;
}

.testimonial-author {
  display: flex;
  align-items: center;
}

.author-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background-size: cover;
  background-position: center;
  margin-right: 1rem;
}

.author-info h4 {
  font-size: 1rem;
  font-weight: 600;
  margin: 0;
  color: #1e293b;
}

.author-info p {
  font-size: 0.875rem;
  color: #64748b;
  margin: 0.25rem 0 0;
}

/* Call to Action Section */
.cta-section {
  padding: 8rem 2rem;
  position: relative;
  overflow: hidden;
}

.cta-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #4f46e5 0%, #9333ea 100%);
  z-index: -1;
}

.cta-content {
  max-width: 700px;
  margin: 0 auto;
  text-align: center;
  color: black;
}

.cta-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
}

.cta-subtitle {
  font-size: 1.25rem;
  opacity: 0.9;
  margin-bottom: 2.5rem;
}

.cta-button {
  font-weight: 600;
  padding: 0 2rem;
  height: 50px;
  font-size: 1.1rem;
  border-radius: 9999px;
  background: white;
  color: #4f46e5;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
  transition: transform 0.2s, box-shadow 0.2s;
}

.cta-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 15px 30px -5px rgba(0, 0, 0, 0.3);
}

/* Media queries for responsive design */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
  }

  .hero-subtitle {
    font-size: 1.25rem;
  }

  .hero-actions {
    flex-direction: column;
    gap: 1rem;
  }

  .section-title {
    font-size: 2rem;
  }

  .process-step {
    flex-direction: column;
  }

  .step-number {
    margin-bottom: 1rem;
    margin-right: 0;
  }

  .process-steps::before {
    display: none;
  }

  .cta-title {
    font-size: 2rem;
  }
}
</style>
