<template>
  <div class="back-cover">
    <!-- Top: small white bar + tagline -->
    <div class="top-block">
      <div class="white-bar"></div>
      <div class="tagline-cn">
        文化取向的宣教<span class="cross">✚</span>國度視野的牧養
      </div>
    </div>

    <!-- Bottom: English bilingual tagline centered -->
    <div class="tagline-en">
      <div>Christian Mission with a Cultural Orientation</div>
      <div>Pastoral ministry with a Vision of Kingdom</div>
    </div>

    <!-- Bottom-right description box -->
    <div class="desc-box">
      衛報是一份關於基督教衛理宗的華文刊物。藉著這份刊物，我們希望向華人世界介紹衛理宗的教義與理念，面對新的挑戰、提供一個多元而活潑的對話空間，讓傳統的智慧在現代社會中得以更新。
    </div>
  </div>
</template>

<style scoped>
.back-cover {
  position: relative;
  width: 100%;
  height: 100%;
  background: #8b7c97;
  color: #ffffff;
  font-family: 'Noto Serif TC', 'Source Han Serif TC', serif;
  overflow: hidden;
  container-type: size;
}

.top-block {
  position: absolute;
  top: 10%;
  left: 14%;
  right: 14%;
}
.white-bar {
  width: 32%;
  height: 0.6cqw;
  background: #ffffff;
  margin-bottom: 2cqw;
  margin-left: 1cqw;
}
.tagline-cn {
  font-size: 3.6cqw;
  letter-spacing: 0.08em;
  color: #ffffff;
  font-weight: 400;
  line-height: 1.4;
}
.cross {
  display: inline-block;
  margin: 0 0.5cqw;
  font-size: 0.85em;
  transform: translateY(-0.3cqw);
}

.tagline-en {
  position: absolute;
  bottom: 11%;
  left: 8%;
  right: 8%;
  text-align: center;
  font-family: 'Georgia', 'Times New Roman', serif;
  font-weight: 700;
  font-style: italic;
  font-size: 2.7cqw;
  line-height: 2;
  color: #f4f0f6;
  letter-spacing: 0.02em;
}

.desc-box {
  position: absolute;
  bottom: 1.5%;
  right: 2%;
  width: 30%;
  background: rgba(70, 60, 78, 0.6);
  padding: 1.5cqw 1.6cqw;
  font-size: 1.65cqw;
  line-height: 1.85;
  color: #f4f0f6;
  text-align: justify;
  letter-spacing: 0.02em;
}
</style>
