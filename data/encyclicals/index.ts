/**
 * Papal Magisterium 資料註冊器
 *
 * 新增一份教宗文件：
 *   1. 在對應世紀子資料夾建立 .ts 檔
 *      （例：21c-francis/laudato-si-2015.ts）
 *   2. 同資料夾放 {slug}-latin.txt / {slug}-english.txt / {slug}-chinese.txt
 *      檔名須對應 metadata 的 textKey
 *   3. 在本檔 import 並加進 ALL_DOCUMENTS
 *   4. 重啟 dev server 即可在 /encyclicals 看到
 */

import type { PapalDocument } from './types'

// ── 21c Francis ──────────────────────────────────────────────
import { laudatoSi2015 } from './21c-francis/laudato-si-2015'
import { fratelliTutti2020 } from './21c-francis/fratelli-tutti-2020'
import { dilexitNos2024 } from './21c-francis/dilexit-nos-2024'
import { lumenFidei2013 } from './21c-francis/lumen-fidei-2013'
import { evangeliiGaudium2013 } from './21c-francis/evangelii-gaudium-2013'

// ── 21c Benedict XVI ────────────────────────────────────────
import { deusCaritasEst2005 } from './21c-benedict-xvi/deus-caritas-est-2005'
import { speSalvi2007 } from './21c-benedict-xvi/spe-salvi-2007'
import { caritasInVeritate2009 } from './21c-benedict-xvi/caritas-in-veritate-2009'

// ── 20c-21c John Paul II ────────────────────────────────────
import { redemptorHominis1979 } from './20c-john-paul-ii/redemptor-hominis-1979'
import { divesInMisericordia1980 } from './20c-john-paul-ii/dives-in-misericordia-1980'
import { laboremExercens1981 } from './20c-john-paul-ii/laborem-exercens-1981'
import { slavorumApostoli1985 } from './20c-john-paul-ii/slavorum-apostoli-1985'
import { dominumEtVivificantem1986 } from './20c-john-paul-ii/dominum-et-vivificantem-1986'
import { redemptorisMater1987 } from './20c-john-paul-ii/redemptoris-mater-1987'
import { sollicitudoReiSocialis1987 } from './20c-john-paul-ii/sollicitudo-rei-socialis-1987'
import { redemptorisMissio1990 } from './20c-john-paul-ii/redemptoris-missio-1990'
import { centesimusAnnus1991 } from './20c-john-paul-ii/centesimus-annus-1991'
import { veritatisSplendor1993 } from './20c-john-paul-ii/veritatis-splendor-1993'
import { evangeliumVitae1995 } from './20c-john-paul-ii/evangelium-vitae-1995'
import { utUnumSint1995 } from './20c-john-paul-ii/ut-unum-sint-1995'
import { fidesEtRatio1998 } from './20c-john-paul-ii/fides-et-ratio-1998'
import { ecclesiaDeEucharistia2003 } from './20c-john-paul-ii/ecclesia-de-eucharistia-2003'

// ── 20c Paul VI ─────────────────────────────────────────────
import { ecclesiamSuam1964 } from './20c-paul-vi/ecclesiam-suam-1964'
import { menseMaio1965 } from './20c-paul-vi/mense-maio-1965'
import { mysteriumFidei1965 } from './20c-paul-vi/mysterium-fidei-1965'
import { christiMatri1966 } from './20c-paul-vi/christi-matri-1966'
import { populorumProgressio1967 } from './20c-paul-vi/populorum-progressio-1967'
import { sacerdotalisCaelibatus1967 } from './20c-paul-vi/sacerdotalis-caelibatus-1967'
import { humanaeVitae1968 } from './20c-paul-vi/humanae-vitae-1968'

// ── 20c John XXIII ──────────────────────────────────────────
import { adPetriCathedram1959 } from './20c-john-xxiii/ad-petri-cathedram-1959'
import { sacerdotiiNostriPrimordia1959 } from './20c-john-xxiii/sacerdotii-nostri-primordia-1959'
import { grataRecordatio1959 } from './20c-john-xxiii/grata-recordatio-1959'
import { princepsPastorum1959 } from './20c-john-xxiii/princeps-pastorum-1959'
import { materEtMagistra1961 } from './20c-john-xxiii/mater-et-magistra-1961'
import { aeternaDeiSapientia1961 } from './20c-john-xxiii/aeterna-dei-sapientia-1961'
import { paenitentiamAgere1962 } from './20c-john-xxiii/paenitentiam-agere-1962'
import { pacemInTerris1963 } from './20c-john-xxiii/pacem-in-terris-1963'

// ── 20c Pius XII ────────────────────────────────────────────
import { summiPontificatus1939 } from './20c-pius-xii/summi-pontificatus-1939'
import { mysticiCorporis1943 } from './20c-pius-xii/mystici-corporis-1943'
import { divinoAfflanteSpiritu1943 } from './20c-pius-xii/divino-afflante-spiritu-1943'
import { mediatorDei1947 } from './20c-pius-xii/mediator-dei-1947'
import { humaniGeneris1950 } from './20c-pius-xii/humani-generis-1950'
import { evangeliiPraecones1951 } from './20c-pius-xii/evangelii-praecones-1951'
import { fulgensCorona1953 } from './20c-pius-xii/fulgens-corona-1953'
import { haurietisAquas1956 } from './20c-pius-xii/haurietis-aquas-1956'

// ── 20c Pius XI ─────────────────────────────────────────────
import { mortaliumAnimos1928 } from './20c-pius-xi/mortalium-animos-1928'
import { diviniIlliusMagistri1929 } from './20c-pius-xi/divini-illius-magistri-1929'
import { castiConnubii1930 } from './20c-pius-xi/casti-connubii-1930'
import { quadragesimoAnno1931 } from './20c-pius-xi/quadragesimo-anno-1931'
import { mitBrennenderSorge1937 } from './20c-pius-xi/mit-brennender-sorge-1937'
import { diviniRedemptoris1937 } from './20c-pius-xi/divini-redemptoris-1937'

// ── 19c Leo XIII ────────────────────────────────────────────
import { aeterniPatris1879 } from './19c-leo-xiii/aeterni-patris-1879'
import { arcanumDivinae1880 } from './19c-leo-xiii/arcanum-divinae-1880'
import { humanumGenus1884 } from './19c-leo-xiii/humanum-genus-1884'
import { immortaleDei1885 } from './19c-leo-xiii/immortale-dei-1885'
import { libertas1888 } from './19c-leo-xiii/libertas-1888'
import { sapientiaeChristianae1890 } from './19c-leo-xiii/sapientiae-christianae-1890'
import { rerumNovarum1891 } from './19c-leo-xiii/rerum-novarum-1891'
import { providentissimusDeus1893 } from './19c-leo-xiii/providentissimus-deus-1893'
import { divinumIlludMunus1897 } from './19c-leo-xiii/divinum-illud-munus-1897'
import { annumSacrum1899 } from './19c-leo-xiii/annum-sacrum-1899'

// ── added: pius-ix (papalencyclicals.net batch) ──
import { quiPluribus1846 } from './19c-pius-ix/qui-pluribus-1846'
import { praedecessoresNostros1847 } from './19c-pius-ix/praedecessores-nostros-1847'
import { ubiPrimum1847 } from './19c-pius-ix/ubi-primum-1847'
import { ubiPrimum1849 } from './19c-pius-ix/ubi-primum-1849'
import { nostisEtNobiscum1849 } from './19c-pius-ix/nostis-et-nobiscum-1849'
import { exultavitCorNostrum1851 } from './19c-pius-ix/exultavit-cor-nostrum-1851'
import { nemoCerteIgnorat1852 } from './19c-pius-ix/nemo-certe-ignorat-1852'
import { probeNoscitisVenerabiles1852 } from './19c-pius-ix/probe-noscitis-venerabiles-1852'
import { interMultiplices1853 } from './19c-pius-ix/inter-multiplices-1853'
import { neminemVestrum1854 } from './19c-pius-ix/neminem-vestrum-1854'
import { optimeNoscitis1854 } from './19c-pius-ix/optime-noscitis-1854'
import { apostolicaeNostraeCaritatis1854 } from './19c-pius-ix/apostolicae-nostrae-caritatis-1854'
import { ineffabilisDeus1854 } from './19c-pius-ix/ineffabilis-deus-1854'
import { optimeNoscitis1855 } from './19c-pius-ix/optime-noscitis-1855'
import { singulariQuidem1856 } from './19c-pius-ix/singulari-quidem-1856'
import { cumNuper1858 } from './19c-pius-ix/cum-nuper-1858'
import { cumSanctaMaterEcclesia1858 } from './19c-pius-ix/cum-sancta-mater-ecclesia-1858'
import { amantissimiRedemptoris1858 } from './19c-pius-ix/amantissimi-redemptoris-1858'
import { quiNuper1859 } from './19c-pius-ix/qui-nuper-1859'
import { nullisCerteVerbis1860 } from './19c-pius-ix/nullis-certe-verbis-1860'
import { amantissimus1862 } from './19c-pius-ix/amantissimus-1862'
import { quantoConficiamurMoerore1863 } from './19c-pius-ix/quanto-conficiamur-moerore-1863'
import { incredibili1863 } from './19c-pius-ix/incredibili-1863'
import { theSyllabusOfErrors1864 } from './19c-pius-ix/the-syllabus-of-errors-1864'
import { maximaeQuidem1864 } from './19c-pius-ix/maximae-quidem-1864'
import { quantaCura1864 } from './19c-pius-ix/quanta-cura-1864'
import { meridionaliAmericae1865 } from './19c-pius-ix/meridionali-americae-1865'
import { levate1867 } from './19c-pius-ix/levate-1867'
import { respicientes1870 } from './19c-pius-ix/respicientes-1870'
import { ubiNos1871 } from './19c-pius-ix/ubi-nos-1871'
import { beneficiaDei1871 } from './19c-pius-ix/beneficia-dei-1871'
import { saepeVenerabilesFratres1871 } from './19c-pius-ix/saepe-venerabiles-fratres-1871'
import { quaeInPatriarchatu1872 } from './19c-pius-ix/quae-in-patriarchatu-1872'
import { quartusSupra1873 } from './19c-pius-ix/quartus-supra-1873'
import { etsiMulta1873 } from './19c-pius-ix/etsi-multa-1873'
import { vixDumANobis1874 } from './19c-pius-ix/vix-dum-a-nobis-1874'
import { omnemSollicitudinem1874 } from './19c-pius-ix/omnem-sollicitudinem-1874'
import { gravibusEcclesiae1874 } from './19c-pius-ix/gravibus-ecclesiae-1874'
import { quodNunquam1875 } from './19c-pius-ix/quod-nunquam-1875'
import { gravesAcDiuturnae1875 } from './19c-pius-ix/graves-ac-diuturnae-1875'

// ── added: gregory-xvi (papalencyclicals.net batch) ──
import { summoIugiterStudio1832 } from './19c-gregory-xvi/summo-iugiter-studio-1832'
import { cumPrimum1832 } from './19c-gregory-xvi/cum-primum-1832'
import { mirariVos1832 } from './19c-gregory-xvi/mirari-vos-1832'
import { quoGraviora1833 } from './19c-gregory-xvi/quo-graviora-1833'
import { singulariNos1834 } from './19c-gregory-xvi/singulari-nos-1834'
import { commissumDivinitus1835 } from './19c-gregory-xvi/commissum-divinitus-1835'
import { inSupremoApostolatus1839 } from './19c-gregory-xvi/in-supremo-apostolatus-1839'
import { probeNostis1840 } from './19c-gregory-xvi/probe-nostis-1840'
import { quasVestro1841 } from './19c-gregory-xvi/quas-vestro-1841'
import { interPraecipuas1844 } from './19c-gregory-xvi/inter-praecipuas-1844'

// ── added: pius-viii (papalencyclicals.net batch) ──
import { traditiHumilitati1829 } from './19c-pius-viii/traditi-humilitati-1829'

// ── added: leo-xii (papalencyclicals.net batch) ──
import { ubiPrimum1824 } from './19c-leo-xii/ubi-primum-1824'
import { quodHocIneunte1824 } from './19c-leo-xii/quod-hoc-ineunte-1824'
import { charitateChristi1825 } from './19c-leo-xii/charitate-christi-1825'
import { quoGraviora1826 } from './19c-leo-xii/quo-graviora-1826'

// ── added: pius-vii (papalencyclicals.net batch) ──
import { diuSatis1800 } from './19c-pius-vii/diu-satis-1800'

// ── added: pius-vi (papalencyclicals.net batch) ──
import { inscrutabile1775 } from './18c-pius-vi/inscrutabile-1775'
import { charitas1791 } from './18c-pius-vi/charitas-1791'
import { ubiLutetiam1792 } from './18c-pius-vi/ubi-lutetiam-1792'

// ── added: clement-xiv (papalencyclicals.net batch) ──
import { decetQuamMaxime1769 } from './18c-clement-xiv/decet-quam-maxime-1769'
import { cumSummi1769 } from './18c-clement-xiv/cum-summi-1769'
import { inscrutabiliDivinaeSapientiae1769 } from './18c-clement-xiv/inscrutabili-divinae-sapientiae-1769'
import { salutisNostrae1774 } from './18c-clement-xiv/salutis-nostrae-1774'

// ── added: clement-xiii (papalencyclicals.net batch) ──
import { aQuoDie1758 } from './18c-clement-xiii/a-quo-die-1758'
import { cumPrimum1759 } from './18c-clement-xiii/cum-primum-1759'
import { appetenteSacro1759 } from './18c-clement-xiii/appetente-sacro-1759'
import { inDominicoAgro1761 } from './18c-clement-xiii/in-dominico-agro-1761'
import { christianaeReipublicae1766 } from './18c-clement-xiii/christianae-reipublicae-1766'
import { summaQuae1768 } from './18c-clement-xiii/summa-quae-1768'

// ── added: benedict-xiv (papalencyclicals.net batch) ──
import { quantaCura1741 } from './18c-benedict-xiv/quanta-cura-1741'
import { nimiamLicentiam1743 } from './18c-benedict-xiv/nimiam-licentiam-1743'
import { vixPervenit1745 } from './18c-benedict-xiv/vix-pervenit-1745'
import { magnaeNobis1748 } from './18c-benedict-xiv/magnae-nobis-1748'
import { annusQuiHunc1749 } from './18c-benedict-xiv/annus-qui-hunc-1749'
import { peregrinantes1749 } from './18c-benedict-xiv/peregrinantes-1749'
import { apostolicaConstitutio1749 } from './18c-benedict-xiv/apostolica-constitutio-1749'
import { aQuoPrimum1751 } from './18c-benedict-xiv/a-quo-primum-1751'
import { cumReligiosi1754 } from './18c-benedict-xiv/cum-religiosi-1754'
import { allataeSunt1755 } from './18c-benedict-xiv/allatae-sunt-1755'
import { exQuo1756 } from './18c-benedict-xiv/ex-quo-1756'
import { exOmnibus1756 } from './18c-benedict-xiv/ex-omnibus-1756'

// ── added: clement-xii (papalencyclicals.net batch) ──
import { inEminenti1738 } from './18c-clement-xii/in-eminenti-1738'

// ── added: clement-xi (papalencyclicals.net batch) ──
import { unigenitus1713 } from './18c-clement-xi/unigenitus-1713'

// ── added: innocent-xi (papalencyclicals.net batch) ──
import { sollicitudoPastoralis1679 } from './17c-innocent-xi/sollicitudo-pastoralis-1679'
import { coelestisPastor1687 } from './17c-innocent-xi/coelestis-pastor-1687'

// ── added: alexander-vii (papalencyclicals.net batch) ──
import { superCathedramPrincipisApostolorum1659 } from './17c-alexander-vii/super-cathedram-principis-apostolorum-1659'

// ── added: clement-viii (papalencyclicals.net batch) ──
import { exSupernaeDispositionisArbitrio1595 } from './16c-clement-viii/ex-supernae-dispositionis-arbitrio-1595'

// ── added: sixtus-v (papalencyclicals.net batch) ──
import { triumphantisHierusalem1590 } from './16c-sixtus-v/triumphantis-hierusalem-1590'

// ── added: pius-v (papalencyclicals.net batch) ──
import { consueveruntRomani1569 } from './16c-pius-v/consueverunt-romani-1569'
import { regnansInExcelsis1570 } from './16c-pius-v/regnans-in-excelsis-1570'
import { quoPrimum1570 } from './16c-pius-v/quo-primum-1570'
import { exponiNobisNuper1571 } from './16c-pius-v/exponi-nobis-nuper-1571'

// ── added: paul-iii (papalencyclicals.net batch) ──
import { sublimisDeus1537 } from './16c-paul-iii/sublimis-deus-1537'
import { inApostolatusCulmine1538 } from './16c-paul-iii/in-apostolatus-culmine-1538'

// ── added: leo-x (papalencyclicals.net batch) ──
import { exsurgeDomine1520 } from './16c-leo-x/exsurge-domine-1520'
import { decetRomanumPontificem1521 } from './16c-leo-x/decet-romanum-pontificem-1521'

// ── added: alexander-vi (papalencyclicals.net batch) ──
import { interCaetera1493 } from './15c-alexander-vi/inter-caetera-1493'

// ── added: sixtus-iv (papalencyclicals.net batch) ──
import { supernaCaelestis1482 } from './15c-sixtus-iv/superna-caelestis-1482'

// ── added: nicholas-v (papalencyclicals.net batch) ──
import { romanusPontifex1455 } from './15c-nicholas-v/romanus-pontifex-1455'

// ── added: eugene-iv (papalencyclicals.net batch) ──
import { sicutDudum1435 } from './15c-eugene-iv/sicut-dudum-1435'

// ── added: benedict-xii (papalencyclicals.net batch) ──
import { benedictusDeus1334 } from './14c-benedict-xii/benedictus-deus-1334'

// ── added: john-xxii (papalencyclicals.net batch) ──
import { quiaQuorundam1316 } from './14c-john-xxii/quia-quorundam-1316'
import { summaProviditAltitudoConsilii1333 } from './14c-john-xxii/summa-providit-altitudo-consilii-1333'

// ── added: clement-v (papalencyclicals.net batch) ──
import { exiviDeParadiso1305 } from './14c-clement-v/exivi-de-paradiso-1305'

// ── added: boniface-viii (papalencyclicals.net batch) ──
import { unamSanctam1302 } from './13c-boniface-viii/unam-sanctam-1302'

// ── added: nicholas-iv (papalencyclicals.net batch) ──
import { supraMontem1289 } from './13c-nicholas-iv/supra-montem-1289'

// ── added: nicholas-iii (papalencyclicals.net batch) ──
import { exiitQuiSeminat1279 } from './13c-nicholas-iii/exiit-qui-seminat-1279'

// ── added: alexander-iv (papalencyclicals.net batch) ──
import { interEaQuaePlacita1255 } from './13c-alexander-iv/inter-ea-quae-placita-1255'
import { petitionibusVestrisBenignumImpertientes1255 } from './13c-alexander-iv/petitionibus-vestris-benignum-impertientes-1255'
import { dignumArbitramurEtCongruum1255 } from './13c-alexander-iv/dignum-arbitramur-et-congruum-1255'

// ── added: innocent-iv (papalencyclicals.net batch) ──
import { quaeHonoremConditorisOmnium1243 } from './13c-innocent-iv/quae-honorem-conditoris-omnium-1243'

// ── added: gregory-x (papalencyclicals.net batch) ──
import { papalProtectionOfTheJews1271 } from './13c-gregory-x/papal-protection-of-the-jews-1271'

// ── added: gregory-ix (papalencyclicals.net batch) ──
import { miraCircaNos1228 } from './13c-gregory-ix/mira-circa-nos-1228'

// ── added: honorius-iii (papalencyclicals.net batch) ──
import { soletAnnuere1226 } from './13c-honorius-iii/solet-annuere-1226'

// ── added: 11c gregory-vii (Wikisource) ──
import { dictatusPapae1075 } from './11c-gregory-vii/dictatus-papae-1075'

// ── added: 5c leo-i (CCEL Schaff NPNF2 Vol 12) ──
import { tomeOfLeo449 } from './5c-leo-i/tome-of-leo-449'

export const ALL_DOCUMENTS: PapalDocument[] = [
  laudatoSi2015,
  fratelliTutti2020,
  dilexitNos2024,
  lumenFidei2013,
  evangeliiGaudium2013,
  deusCaritasEst2005,
  speSalvi2007,
  caritasInVeritate2009,
  redemptorHominis1979,
  divesInMisericordia1980,
  laboremExercens1981,
  slavorumApostoli1985,
  dominumEtVivificantem1986,
  redemptorisMater1987,
  sollicitudoReiSocialis1987,
  redemptorisMissio1990,
  centesimusAnnus1991,
  veritatisSplendor1993,
  evangeliumVitae1995,
  utUnumSint1995,
  fidesEtRatio1998,
  ecclesiaDeEucharistia2003,
  // Paul VI
  ecclesiamSuam1964,
  menseMaio1965,
  mysteriumFidei1965,
  christiMatri1966,
  populorumProgressio1967,
  sacerdotalisCaelibatus1967,
  humanaeVitae1968,
  // John XXIII
  adPetriCathedram1959,
  sacerdotiiNostriPrimordia1959,
  grataRecordatio1959,
  princepsPastorum1959,
  materEtMagistra1961,
  aeternaDeiSapientia1961,
  paenitentiamAgere1962,
  pacemInTerris1963,
  // Pius XII
  summiPontificatus1939,
  mysticiCorporis1943,
  divinoAfflanteSpiritu1943,
  mediatorDei1947,
  humaniGeneris1950,
  evangeliiPraecones1951,
  fulgensCorona1953,
  haurietisAquas1956,
  // Pius XI
  mortaliumAnimos1928,
  diviniIlliusMagistri1929,
  castiConnubii1930,
  quadragesimoAnno1931,
  mitBrennenderSorge1937,
  diviniRedemptoris1937,
  // Leo XIII
  aeterniPatris1879,
  arcanumDivinae1880,
  humanumGenus1884,
  immortaleDei1885,
  libertas1888,
  sapientiaeChristianae1890,
  rerumNovarum1891,
  providentissimusDeus1893,
  divinumIlludMunus1897,
  annumSacrum1899,
  // ── added: pius-ix ──
  nostisEtNobiscum1849,
  exultavitCorNostrum1851,
  nemoCerteIgnorat1852,
  probeNoscitisVenerabiles1852,
  interMultiplices1853,
  neminemVestrum1854,
  optimeNoscitis1854,
  apostolicaeNostraeCaritatis1854,
  ineffabilisDeus1854,
  optimeNoscitis1855,
  singulariQuidem1856,
  cumNuper1858,
  cumSanctaMaterEcclesia1858,
  amantissimiRedemptoris1858,
  quiNuper1859,
  nullisCerteVerbis1860,
  amantissimus1862,
  quantoConficiamurMoerore1863,
  incredibili1863,
  theSyllabusOfErrors1864,
  maximaeQuidem1864,
  quantaCura1864,
  meridionaliAmericae1865,
  levate1867,
  respicientes1870,
  ubiNos1871,
  beneficiaDei1871,
  saepeVenerabilesFratres1871,
  quaeInPatriarchatu1872,
  quartusSupra1873,
  etsiMulta1873,
  vixDumANobis1874,
  omnemSollicitudinem1874,
  gravibusEcclesiae1874,
  quodNunquam1875,
  gravesAcDiuturnae1875,
  ubiPrimum1847,
  ubiPrimum1849,
  quiPluribus1846,
  praedecessoresNostros1847,
  // ── added: gregory-xvi ──
  summoIugiterStudio1832,
  cumPrimum1832,
  mirariVos1832,
  quoGraviora1833,
  singulariNos1834,
  commissumDivinitus1835,
  inSupremoApostolatus1839,
  probeNostis1840,
  quasVestro1841,
  interPraecipuas1844,
  // ── added: pius-viii ──
  traditiHumilitati1829,
  // ── added: leo-xii ──
  ubiPrimum1824,
  quodHocIneunte1824,
  charitateChristi1825,
  quoGraviora1826,
  // ── added: pius-vii ──
  diuSatis1800,
  // ── added: pius-vi ──
  inscrutabile1775,
  charitas1791,
  ubiLutetiam1792,
  // ── added: clement-xiv ──
  decetQuamMaxime1769,
  cumSummi1769,
  inscrutabiliDivinaeSapientiae1769,
  salutisNostrae1774,
  // ── added: clement-xiii ──
  aQuoDie1758,
  cumPrimum1759,
  appetenteSacro1759,
  inDominicoAgro1761,
  christianaeReipublicae1766,
  summaQuae1768,
  // ── added: benedict-xiv ──
  quantaCura1741,
  nimiamLicentiam1743,
  vixPervenit1745,
  magnaeNobis1748,
  annusQuiHunc1749,
  peregrinantes1749,
  apostolicaConstitutio1749,
  aQuoPrimum1751,
  cumReligiosi1754,
  allataeSunt1755,
  exQuo1756,
  exOmnibus1756,
  // ── added: clement-xii ──
  inEminenti1738,
  // ── added: clement-xi ──
  unigenitus1713,
  // ── added: innocent-xi ──
  sollicitudoPastoralis1679,
  coelestisPastor1687,
  // ── added: alexander-vii ──
  superCathedramPrincipisApostolorum1659,
  // ── added: clement-viii ──
  exSupernaeDispositionisArbitrio1595,
  // ── added: sixtus-v ──
  triumphantisHierusalem1590,
  // ── added: pius-v ──
  consueveruntRomani1569,
  regnansInExcelsis1570,
  quoPrimum1570,
  exponiNobisNuper1571,
  // ── added: paul-iii ──
  sublimisDeus1537,
  inApostolatusCulmine1538,
  // ── added: leo-x ──
  exsurgeDomine1520,
  decetRomanumPontificem1521,
  // ── added: alexander-vi ──
  interCaetera1493,
  // ── added: sixtus-iv ──
  supernaCaelestis1482,
  // ── added: nicholas-v ──
  romanusPontifex1455,
  // ── added: eugene-iv ──
  sicutDudum1435,
  // ── added: benedict-xii ──
  benedictusDeus1334,
  // ── added: john-xxii ──
  quiaQuorundam1316,
  summaProviditAltitudoConsilii1333,
  // ── added: clement-v ──
  exiviDeParadiso1305,
  // ── added: boniface-viii ──
  unamSanctam1302,
  // ── added: nicholas-iv ──
  supraMontem1289,
  // ── added: nicholas-iii ──
  exiitQuiSeminat1279,
  // ── added: alexander-iv ──
  interEaQuaePlacita1255,
  petitionibusVestrisBenignumImpertientes1255,
  dignumArbitramurEtCongruum1255,
  // ── added: innocent-iv ──
  quaeHonoremConditorisOmnium1243,
  // ── added: gregory-x ──
  papalProtectionOfTheJews1271,
  // ── added: gregory-ix ──
  miraCircaNos1228,
  // ── added: honorius-iii ──
  soletAnnuere1226,
  // ── added: 11c gregory-vii ──
  dictatusPapae1075,
  // ── added: 5c leo-i ──
  tomeOfLeo449,
]

export function findDocument(slug: string): PapalDocument | undefined {
  return ALL_DOCUMENTS.find(d => d.slug === slug)
}

export function documentsByPope(popeSlug: string): PapalDocument[] {
  return ALL_DOCUMENTS
    .filter(d => d.popeSlug === popeSlug)
    .sort((a, b) => a.promulgationDate.localeCompare(b.promulgationDate))
}

/** 按世紀分組（新→舊）；每組內按文件年份新→舊排序 */
export function documentsByCentury(): { century: number; docs: PapalDocument[] }[] {
  const map = new Map<number, PapalDocument[]>()
  for (const d of ALL_DOCUMENTS) {
    if (!map.has(d.century)) map.set(d.century, [])
    map.get(d.century)!.push(d)
  }
  return [...map.entries()]
    .sort((a, b) => b[0] - a[0])
    .map(([century, docs]) => ({
      century,
      docs: docs.sort((a, b) => b.promulgationDate.localeCompare(a.promulgationDate)),
    }))
}

export function documentsInCentury(century: number): PapalDocument[] {
  return ALL_DOCUMENTS
    .filter(d => d.century === century)
    .sort((a, b) => b.promulgationDate.localeCompare(a.promulgationDate))
}

/** 單一教宗在指定世紀的文件數（用來在世紀頁顯示教宗的「本世紀著作數」chip） */
export function documentCountForPopeInCentury(popeSlug: string, century: number): number {
  return ALL_DOCUMENTS.filter(d => d.popeSlug === popeSlug && d.century === century).length
}

export * from './types'
export * from './popes-catalog'
