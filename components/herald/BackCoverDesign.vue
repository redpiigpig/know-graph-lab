<template>
  <div class="back-cover">
    <!-- Top white bar + tagline -->
    <div class="top-bar"></div>
    <div class="tagline-cn">
      文化取向的宣教<span class="cross">✚</span>國度視野的牧養
    </div>

    <!-- Bottom english tagline -->
    <div class="tagline-en">
      <div>Christian Mission with a Cultural Orientation</div>
      <div>Pastoral ministry with a Vision of Kingdom</div>
    </div>

    <!-- Description box bottom-right -->
    <div class="desc-box">
      <div>
        衛報是一份關於基督教衛理宗的華文刊物。
        藉著這份刊物，我們希望向華人世界介紹衛
        理宗的教義與理念，面對新的挑戰、提供一
        個多元而活潑的對話空間，讓傳統的智慧在
        現代社會中得以更新。
      </div>
    </div>
  </div>
</template>

<style scoped>
.back-cover {
  position: relative;
  width: 100%;
  height: 100%;
  background: linear-gradient(180deg, #8b7c97 0%, #7c6d88 50%, #8b7c97 100%);
  color: #ffffff;
  font-family: 'Noto Serif TC', 'Source Han Serif TC', serif;
  overflow: hidden;
  container-type: size;
}

.top-bar {
  position: absolute;
  top: 8%;
  left: 14%;
  width: 38%;
  height: 0.8cqw;
  background: #ffffff;
}

.tagline-cn {
  position: absolute;
  top: 12%;
  left: 14%;
  font-size: 3.8cqw;
  letter-spacing: 0.1em;
  color: #ffffff;
  font-weight: 500;
}
.cross {
  display: inline-block;
  margin: 0 0.6cqw;
  color: #ffffff;
  transform: translateY(-0.2cqw);
}

.tagline-en {
  position: absolute;
  bottom: 14%;
  left: 14%;
  right: 14%;
  text-align: center;
  font-family: 'Georgia', serif;
  font-weight: 700;
  font-size: 2.6cqw;
  line-height: 1.8;
  color: #d8d3dd;
}

.desc-box {
  position: absolute;
  bottom: 3%;
  right: 4%;
  width: 30%;
  background: rgba(60, 50, 70, 0.5);
  border: 0.15cqw solid rgba(255, 255, 255, 0.3);
  padding: 1.5cqw 1.8cqw;
  font-size: 1.7cqw;
  line-height: 1.7;
  color: #f0ebf3;
}
</style>
