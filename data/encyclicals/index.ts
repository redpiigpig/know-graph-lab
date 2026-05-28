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

// ── 20c Benedict XV ─────────────────────────────────────────
import { adBeatissimiApostolorum1914 } from './20c-benedict-xv/ad-beatissimi-apostolorum-1914'
import { humaniGenerisRedemptionem1917 } from './20c-benedict-xv/humani-generis-redemptionem-1917'
import { quodIamDiu1918 } from './20c-benedict-xv/quod-iam-diu-1918'
import { inHacTanta1919 } from './20c-benedict-xv/in-hac-tanta-1919'
import { paternoIamDiu1919 } from './20c-benedict-xv/paterno-iam-diu-1919'
import { maximumIllud1919 } from './20c-benedict-xv/maximum-illud-1919'
import { pacemDeiMunusPulcherrimum1920 } from './20c-benedict-xv/pacem-dei-munus-pulcherrimum-1920'
import { spiritusParaclitus1920 } from './20c-benedict-xv/spiritus-paraclitus-1920'
import { principiApostolorumPetro1920 } from './20c-benedict-xv/principi-apostolorum-petro-1920'
import { annusIamPlenus1920 } from './20c-benedict-xv/annus-iam-plenus-1920'
import { sacraPropediem1921 } from './20c-benedict-xv/sacra-propediem-1921'
import { inPraeclaraSummorum1921 } from './20c-benedict-xv/in-praeclara-summorum-1921'
import { faustoAppetenteDie1921 } from './20c-benedict-xv/fausto-appetente-die-1921'

// ── 20c Pius X ──────────────────────────────────────────────
import { eSupremi1903 } from './20c-pius-x/e-supremi-1903'
import { adDiemIllumLaetissimum1904 } from './20c-pius-x/ad-diem-illum-laetissimum-1904'
import { iucundaSane1904 } from './20c-pius-x/iucunda-sane-1904'
import { acerboNimis1905 } from './20c-pius-x/acerbo-nimis-1905'
import { ilFermoProposito1905 } from './20c-pius-x/il-fermo-proposito-1905'
import { vehementerNos1906 } from './20c-pius-x/vehementer-nos-1906'
import { tribusCirciter1906 } from './20c-pius-x/tribus-circiter-1906'
import { pieniLAnimo1906 } from './20c-pius-x/pieni-l-animo-1906'
import { gravissimoOfficiiMunere1906 } from './20c-pius-x/gravissimo-officii-munere-1906'
import { uneFoisEncore1907 } from './20c-pius-x/une-fois-encore-1907'
import { pascendiDominiciGregis1907 } from './20c-pius-x/pascendi-dominici-gregis-1907'
import { communiumRerum1909 } from './20c-pius-x/communium-rerum-1909'
import { editaeSaepe1910 } from './20c-pius-x/editae-saepe-1910'
import { iamdudum1911 } from './20c-pius-x/iamdudum-1911'
import { lacrimabiliStatu1912 } from './20c-pius-x/lacrimabili-statu-1912'
import { singulariQuadam1912 } from './20c-pius-x/singulari-quadam-1912'

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

// ── 2026-05-28 B 區 (curia) — vatican.va 信理部 ──
import { dignitasInfinita2024 } from './21c-francis/dignitas-infinita-2024'
import { iuvenescitEcclesia2016 } from './21c-francis/iuvenescit-ecclesia-2016'


// ── 2026-05-28 hsscol BC 批次 — 20c-john-paul-ii ──
import { catechesiTradendae1979 } from './20c-john-paul-ii/catechesi-tradendae-1979'
import { hsscolP1651979 } from './20c-john-paul-ii/hsscol-p165-1979'
import { hsscolP1682002 } from './20c-john-paul-ii/hsscol-p168-2002'
import { hsscolP1691981 } from './20c-john-paul-ii/hsscol-p169-1981'
import { familiarisConsortio1981 } from './20c-john-paul-ii/familiaris-consortio-1981'
import { hsscolP1721983 } from './20c-john-paul-ii/hsscol-p172-1983'
import { reconciliatioEtPaenitentia1984 } from './20c-john-paul-ii/reconciliatio-et-paenitentia-1984'
import { hsscolP1741984 } from './20c-john-paul-ii/hsscol-p174-1984'
import { hsscolP1751984 } from './20c-john-paul-ii/hsscol-p175-1984'
import { hsscolP1781987 } from './20c-john-paul-ii/hsscol-p178-1987'
import { hsscolP1791987 } from './20c-john-paul-ii/hsscol-p179-1987'
import { hsscolP1811988 } from './20c-john-paul-ii/hsscol-p181-1988'
import { hsscolP1821988 } from './20c-john-paul-ii/hsscol-p182-1988'
import { hsscolP1831988 } from './20c-john-paul-ii/hsscol-p183-1988'
import { redemptorisCustos1989 } from './20c-john-paul-ii/redemptoris-custos-1989'
import { hsscolP1852002 } from './20c-john-paul-ii/hsscol-p185-2002'
import { pastoresDaboVobis1992 } from './20c-john-paul-ii/pastores-dabo-vobis-1992'
import { hsscolP1881993 } from './20c-john-paul-ii/hsscol-p188-1993'
import { ordinatioSacerdotalis1994 } from './20c-john-paul-ii/ordinatio-sacerdotalis-1994'
import { hsscolP1931995 } from './20c-john-paul-ii/hsscol-p193-1995'
import { hsscolP1941995 } from './20c-john-paul-ii/hsscol-p194-1995'
import { hsscolP1961995 } from './20c-john-paul-ii/hsscol-p196-1995'
import { hsscolP1971996 } from './20c-john-paul-ii/hsscol-p197-1996'
import { vitaConsecrata1996 } from './20c-john-paul-ii/vita-consecrata-1996'
import { hsscolP1991998 } from './20c-john-paul-ii/hsscol-p199-1998'
import { hsscolP2001998 } from './20c-john-paul-ii/hsscol-p200-1998'
import { hsscolP2011998 } from './20c-john-paul-ii/hsscol-p201-1998'
import { hsscolP2021998 } from './20c-john-paul-ii/hsscol-p202-1998'
import { adTuendamFidem1998 } from './20c-john-paul-ii/ad-tuendam-fidem-1998'
import { fideiDepositum1992 } from './20c-john-paul-ii/fidei-depositum-1992'
import { hsscolP2122001 } from './20c-john-paul-ii/hsscol-p212-2001'
import { hsscolP2132003 } from './20c-john-paul-ii/hsscol-p213-2003'
import { misericordiaDei2002 } from './21c-john-paul-ii/misericordia-dei-2002'
import { hsscolP2152004 } from './20c-john-paul-ii/hsscol-p215-2004'
import { hsscolP2171993 } from './20c-john-paul-ii/hsscol-p217-1993'
import { hsscolP2181999 } from './20c-john-paul-ii/hsscol-p218-1999'
import { hsscolP2192001 } from './20c-john-paul-ii/hsscol-p219-2001'
import { hsscolP2202004 } from './20c-john-paul-ii/hsscol-p220-2004'
import { hsscolP2232002 } from './20c-john-paul-ii/hsscol-p223-2002'
import { hsscolP2242005 } from './20c-john-paul-ii/hsscol-p224-2005'
import { hsscolP2252005 } from './20c-john-paul-ii/hsscol-p225-2005'
import { hsscolP2262005 } from './20c-john-paul-ii/hsscol-p226-2005'
import { hsscolP2302004 } from './20c-john-paul-ii/hsscol-p230-2004'
import { hsscolP2312004 } from './20c-john-paul-ii/hsscol-p231-2004'
import { hsscolP2322004 } from './20c-john-paul-ii/hsscol-p232-2004'
import { hsscolP2332004 } from './20c-john-paul-ii/hsscol-p233-2004'
import { hsscolP2341991 } from './20c-john-paul-ii/hsscol-p234-1991'
import { hsscolP2431994 } from './20c-john-paul-ii/hsscol-p243-1994'
import { hsscolP2442003 } from './20c-john-paul-ii/hsscol-p244-2003'
import { hsscolP2452002 } from './20c-john-paul-ii/hsscol-p245-2002'
import { hsscolP2462001 } from './20c-john-paul-ii/hsscol-p246-2001'
import { hsscolP2472005 } from './20c-john-paul-ii/hsscol-p247-2005'
import { hsscolP2492000 } from './20c-john-paul-ii/hsscol-p249-2000'
import { hsscolP2502001 } from './20c-john-paul-ii/hsscol-p250-2001'
import { hsscolP2512007 } from './20c-john-paul-ii/hsscol-p251-2007'
import { exCordeEcclesiae1990 } from './20c-john-paul-ii/ex-corde-ecclesiae-1990'
import { hsscolP2702009 } from './20c-john-paul-ii/hsscol-p270-2009'
import { hsscolP2772010 } from './20c-john-paul-ii/hsscol-p277-2010'
import { hsscolP2992003 } from './20c-john-paul-ii/hsscol-p299-2003'
import { hsscolP3002003 } from './20c-john-paul-ii/hsscol-p300-2003'
import { hsscolP3451980 } from './20c-john-paul-ii/hsscol-p345-1980'
import { hsscolP3501982 } from './20c-john-paul-ii/hsscol-p350-1982'
import { hsscolP3531995 } from './20c-john-paul-ii/hsscol-p353-1995'
import { hsscolP3622002 } from './20c-john-paul-ii/hsscol-p362-2002'
import { hsscolP3632002 } from './20c-john-paul-ii/hsscol-p363-2002'
import { hsscolP3642002 } from './20c-john-paul-ii/hsscol-p364-2002'
import { hsscolP3652000 } from './20c-john-paul-ii/hsscol-p365-2000'
import { hsscolP3661999 } from './20c-john-paul-ii/hsscol-p366-1999'
import { hsscolP3672004 } from './20c-john-paul-ii/hsscol-p367-2004'
import { hsscolP3831999 } from './20c-john-paul-ii/hsscol-p383-1999'
import { hsscolP3841997 } from './20c-john-paul-ii/hsscol-p384-1997'
import { hsscolP3852003 } from './20c-john-paul-ii/hsscol-p385-2003'
import { hsscolP3862003 } from './20c-john-paul-ii/hsscol-p386-2003'
import { hsscolP3871997 } from './20c-john-paul-ii/hsscol-p387-1997'
import { theHolySee1994 } from './20c-john-paul-ii/the-holy-see-1994'

// ── 2026-05-28 hsscol BC 批次 — 20c-paul-vi ──
import { apostolicConstitutionOnTheFastAmpAbstinence1966 } from './20c-paul-vi/apostolic-constitution-on-the-fast-amp-abstinence-1966'
import { christianoGaudio1975 } from './20c-paul-vi/christiano-gaudio-1975'
import { hsscolP0011967 } from './20c-paul-vi/hsscol-p001-1967'
import { hsscolP0031971 } from './20c-paul-vi/hsscol-p003-1971'
import { hsscolP0041970 } from './20c-paul-vi/hsscol-p004-1970'
import { hsscolP0051971 } from './20c-paul-vi/hsscol-p005-1971'
import { hsscolP0061971 } from './20c-paul-vi/hsscol-p006-1971'
import { hsscolP0071971 } from './20c-paul-vi/hsscol-p007-1971'
import { hsscolP0081971 } from './20c-paul-vi/hsscol-p008-1971'
import { hsscolP0091971 } from './20c-paul-vi/hsscol-p009-1971'
import { hsscolP0101971 } from './20c-paul-vi/hsscol-p010-1971'
import { hsscolP0111970 } from './20c-paul-vi/hsscol-p011-1970'
import { hsscolP0171967 } from './20c-paul-vi/hsscol-p017-1967'
import { hsscolP0181970 } from './20c-paul-vi/hsscol-p018-1970'
import { hsscolP0201967 } from './20c-paul-vi/hsscol-p020-1967'
import { hsscolP0221968 } from './20c-paul-vi/hsscol-p022-1968'
import { sacramLiturgiam1964 } from './20c-paul-vi/sacram-liturgiam-1964'
import { proCompertoSane1967 } from './20c-paul-vi/pro-comperto-sane-1967'
import { hsscolP0261969 } from './20c-paul-vi/hsscol-p026-1969'
import { studiaLatinitatis1964 } from './20c-paul-vi/studia-latinitatis-1964'
import { hsscolP0401970 } from './20c-paul-vi/hsscol-p040-1970'
import { hsscolP0411970 } from './20c-paul-vi/hsscol-p041-1970'
import { hsscolP0421970 } from './20c-paul-vi/hsscol-p042-1970'
import { hsscolP0431970 } from './20c-paul-vi/hsscol-p043-1970'
import { hsscolP0441970 } from './20c-paul-vi/hsscol-p044-1970'
import { hsscolP0451970 } from './20c-paul-vi/hsscol-p045-1970'
import { hsscolP0461970 } from './20c-paul-vi/hsscol-p046-1970'
import { hsscolP0471970 } from './20c-paul-vi/hsscol-p047-1970'
import { hsscolP0561968 } from './20c-paul-vi/hsscol-p056-1968'
import { hsscolP0571969 } from './20c-paul-vi/hsscol-p057-1969'
import { hsscolP0581970 } from './20c-paul-vi/hsscol-p058-1970'
import { hsscolP0591970 } from './20c-paul-vi/hsscol-p059-1970'
import { hsscolP0601970 } from './20c-paul-vi/hsscol-p060-1970'
import { hsscolP0611970 } from './20c-paul-vi/hsscol-p061-1970'
import { hsscolP0621970 } from './20c-paul-vi/hsscol-p062-1970'
import { hsscolP0631970 } from './20c-paul-vi/hsscol-p063-1970'
import { hsscolP0641970 } from './20c-paul-vi/hsscol-p064-1970'
import { hsscolP0651970 } from './20c-paul-vi/hsscol-p065-1970'
import { hsscolP0721968 } from './20c-paul-vi/hsscol-p072-1968'
import { hsscolP1711983 } from './20c-paul-vi/hsscol-p171-1983'
import { hsscolP4581973 } from './20c-paul-vi/hsscol-p458-1973'
import { hsscolP4591970 } from './20c-paul-vi/hsscol-p459-1970'
import { regiminiEcclesiae1967 } from './20c-paul-vi/regimini-ecclesiae-1967'
import { sacrarumIndulgentiarumRecognitio1967 } from './20c-paul-vi/sacrarum-indulgentiarum-recognitio-1967'
import { sacrumDiaconatus1967 } from './20c-paul-vi/sacrum-diaconatus-1967'

// ── 2026-05-28 hsscol BC 批次 — 20c-pius-xi ──
import { deAcrisMissionibusProvehendis1926 } from './20c-pius-xi/de-acris-missionibus-provehendis-1926'
import { diviniMagistri1929 } from './20c-pius-xi/divini-magistri-1929'
import { hsscolP0761931 } from './20c-pius-xi/hsscol-p076-1931'
import { hsscolP0771935 } from './20c-pius-xi/hsscol-p077-1935'
import { hsscolP0781922 } from './20c-pius-xi/hsscol-p078-1922'
import { hsscolP0801926 } from './20c-pius-xi/hsscol-p080-1926'

// ── 2026-05-28 hsscol BC 批次 — 20c-pius-xii ──
import { hsscolP0941939 } from './20c-pius-xii/hsscol-p094-1939'
import { hsscolP0951940 } from './20c-pius-xii/hsscol-p095-1940'
import { hsscolP0961940 } from './20c-pius-xii/hsscol-p096-1940'
import { hsscolP0971940 } from './20c-pius-xii/hsscol-p097-1940'
import { hsscolP0981940 } from './20c-pius-xii/hsscol-p098-1940'
import { hsscolP1001941 } from './20c-pius-xii/hsscol-p100-1941'
import { hsscolP1041943 } from './20c-pius-xii/hsscol-p104-1943'
import { hsscolP1051951 } from './20c-pius-xii/hsscol-p105-1951'
import { hsscolP1071943 } from './20c-pius-xii/hsscol-p107-1943'
import { hsscolP1081943 } from './20c-pius-xii/hsscol-p108-1943'
import { hsscolP1091944 } from './20c-pius-xii/hsscol-p109-1944'
import { hsscolP1101944 } from './20c-pius-xii/hsscol-p110-1944'
import { hsscolP1111945 } from './20c-pius-xii/hsscol-p111-1945'
import { hsscolP1121945 } from './20c-pius-xii/hsscol-p112-1945'
import { hsscolP1131945 } from './20c-pius-xii/hsscol-p113-1945'
import { hsscolP1141946 } from './20c-pius-xii/hsscol-p114-1946'
import { hsscolP1151946 } from './20c-pius-xii/hsscol-p115-1946'
import { hsscolP1171947 } from './20c-pius-xii/hsscol-p117-1947'
import { hsscolP1181947 } from './20c-pius-xii/hsscol-p118-1947'
import { hsscolP1191948 } from './20c-pius-xii/hsscol-p119-1948'
import { hsscolP1201949 } from './20c-pius-xii/hsscol-p120-1949'
import { hsscolP1211949 } from './20c-pius-xii/hsscol-p121-1949'
import { hsscolP1221951 } from './20c-pius-xii/hsscol-p122-1951'
import { hsscolP1231951 } from './20c-pius-xii/hsscol-p123-1951'
import { hsscolP1241956 } from './20c-pius-xii/hsscol-p124-1956'
import { hsscolP1251956 } from './20c-pius-xii/hsscol-p125-1956'
import { hsscolP1261958 } from './20c-pius-xii/hsscol-p126-1958'
import { hsscolP1271949 } from './20c-pius-xii/hsscol-p127-1949'
import { hsscolP1281950 } from './20c-pius-xii/hsscol-p128-1950'
import { hsscolP1292002 } from './20c-pius-xii/hsscol-p129-2002'
import { hsscolP1301951 } from './20c-pius-xii/hsscol-p130-1951'
import { hsscolP1321952 } from './20c-pius-xii/hsscol-p132-1952'
import { hsscolP1331952 } from './20c-pius-xii/hsscol-p133-1952'
import { hsscolP1342002 } from './20c-pius-xii/hsscol-p134-2002'
import { christusDominus1953 } from './20c-pius-xii/christus-dominus-1953'
import { cupimusImprimis1952 } from './20c-pius-xii/cupimus-imprimis-1952'
import { hsscolP1381953 } from './20c-pius-xii/hsscol-p138-1953'
import { hsscolP1391953 } from './20c-pius-xii/hsscol-p139-1953'
import { hsscolP1401953 } from './20c-pius-xii/hsscol-p140-1953'
import { hsscolP1411954 } from './20c-pius-xii/hsscol-p141-1954'
import { sacraVirginitas1954 } from './20c-pius-xii/sacra-virginitas-1954'
import { hsscolP1431954 } from './20c-pius-xii/hsscol-p143-1954'
import { hsscolP1461955 } from './20c-pius-xii/hsscol-p146-1955'
import { hsscolP1471955 } from './20c-pius-xii/hsscol-p147-1955'
import { hsscolP1481955 } from './20c-pius-xii/hsscol-p148-1955'
import { hsscolP1491955 } from './20c-pius-xii/hsscol-p149-1955'
import { hsscolP1501956 } from './20c-pius-xii/hsscol-p150-1956'
import { hsscolP1541957 } from './20c-pius-xii/hsscol-p154-1957'
import { hsscolP1551957 } from './20c-pius-xii/hsscol-p155-1957'
import { hsscolP1561957 } from './20c-pius-xii/hsscol-p156-1957'
import { hsscolP1571957 } from './20c-pius-xii/hsscol-p157-1957'
import { hsscolP1581957 } from './20c-pius-xii/hsscol-p158-1957'
import { hsscolP1591957 } from './20c-pius-xii/hsscol-p159-1957'
import { mirandaProrsus1957 } from './20c-pius-xii/miranda-prorsus-1957'
import { hsscolP1611958 } from './20c-pius-xii/hsscol-p161-1958'
import { hsscolP1621958 } from './20c-pius-xii/hsscol-p162-1958'
import { hsscolP2061955 } from './20c-pius-xii/hsscol-p206-1955'
import { hsscolP2071956 } from './20c-pius-xii/hsscol-p207-1956'
import { hsscolP2081957 } from './20c-pius-xii/hsscol-p208-1957'
import { hsscolP2091958 } from './20c-pius-xii/hsscol-p209-1958'
import { laSolennita1941 } from './20c-pius-xii/la-solennita-1941'
import { votreVisite1956 } from './20c-pius-xii/votre-visite-1956'

// ── 2026-05-28 hsscol BC 批次 — 21c-benedict-xvi ──
import { hsscolP2272006 } from './21c-benedict-xvi/hsscol-p227-2006'
import { hsscolP2282006 } from './21c-benedict-xvi/hsscol-p228-2006'
import { hsscolP2292006 } from './21c-benedict-xvi/hsscol-p229-2006'
import { hsscolP2392006 } from './21c-benedict-xvi/hsscol-p239-2006'
import { hsscolP2402005 } from './21c-benedict-xvi/hsscol-p240-2005'
import { hsscolP2412007 } from './21c-benedict-xvi/hsscol-p241-2007'
import { hsscolP2422007 } from './21c-benedict-xvi/hsscol-p242-2007'
import { hsscolP2482006 } from './21c-benedict-xvi/hsscol-p248-2006'
import { hsscolP2602005 } from './21c-benedict-xvi/hsscol-p260-2005'
import { hsscolP2612007 } from './21c-benedict-xvi/hsscol-p261-2007'
import { hsscolP2622005 } from './21c-benedict-xvi/hsscol-p262-2005'
import { hsscolP2642006 } from './21c-benedict-xvi/hsscol-p264-2006'
import { hsscolP2652008 } from './21c-benedict-xvi/hsscol-p265-2008'
import { hsscolP2661970 } from './21c-benedict-xvi/hsscol-p266-1970'
import { hsscolP2672009 } from './21c-benedict-xvi/hsscol-p267-2009'
import { hsscolP2682009 } from './21c-benedict-xvi/hsscol-p268-2009'
import { hsscolP2692006 } from './21c-benedict-xvi/hsscol-p269-2006'
import { hsscolP2712005 } from './21c-benedict-xvi/hsscol-p271-2005'
import { hsscolP2722006 } from './21c-benedict-xvi/hsscol-p272-2006'
import { hsscolP2732009 } from './21c-benedict-xvi/hsscol-p273-2009'
import { hsscolP2752010 } from './21c-benedict-xvi/hsscol-p275-2010'
import { hsscolP2762010 } from './21c-benedict-xvi/hsscol-p276-2010'
import { hsscolP2782009 } from './21c-benedict-xvi/hsscol-p278-2009'
import { hsscolP2792011 } from './21c-benedict-xvi/hsscol-p279-2011'
import { hsscolP2802011 } from './21c-benedict-xvi/hsscol-p280-2011'
import { hsscolP2812010 } from './21c-benedict-xvi/hsscol-p281-2010'
import { hsscolP2822011 } from './21c-benedict-xvi/hsscol-p282-2011'
import { hsscolP2842011 } from './21c-benedict-xvi/hsscol-p284-2011'
import { hsscolP2852011 } from './21c-benedict-xvi/hsscol-p285-2011'
import { hsscolP2862011 } from './21c-benedict-xvi/hsscol-p286-2011'
import { hsscolP2872010 } from './21c-benedict-xvi/hsscol-p287-2010'
import { hsscolP2882012 } from './21c-benedict-xvi/hsscol-p288-2012'
import { hsscolP2892012 } from './21c-benedict-xvi/hsscol-p289-2012'
import { hsscolP2902012 } from './21c-benedict-xvi/hsscol-p290-2012'
import { hsscolP2912012 } from './21c-benedict-xvi/hsscol-p291-2012'
import { hsscolP2922012 } from './21c-benedict-xvi/hsscol-p292-2012'
import { hsscolP2932012 } from './21c-benedict-xvi/hsscol-p293-2012'
import { hsscolP2942012 } from './21c-benedict-xvi/hsscol-p294-2012'
import { hsscolP2952011 } from './21c-benedict-xvi/hsscol-p295-2011'
import { hsscolP2962013 } from './21c-benedict-xvi/hsscol-p296-2013'
import { hsscolP2972012 } from './21c-benedict-xvi/hsscol-p297-2012'
import { hsscolP2982013 } from './21c-benedict-xvi/hsscol-p298-2013'
import { hsscolP3012013 } from './21c-benedict-xvi/hsscol-p301-2013'
import { hsscolP3052013 } from './21c-benedict-xvi/hsscol-p305-2013'
import { hsscolP3142007 } from './21c-benedict-xvi/hsscol-p314-2007'
import { hsscolP3192013 } from './21c-benedict-xvi/hsscol-p319-2013'
import { hsscolP4792009 } from './21c-benedict-xvi/hsscol-p479-2009'

// ── 2026-05-28 hsscol BC 批次 — 21c-francis ──
import { chineseRegionalBishops2017 } from './21c-francis/chinese-regional-bishops-2017'
import { hsscolP3032014 } from './21c-francis/hsscol-p303-2014'
import { hsscolP3042014 } from './21c-francis/hsscol-p304-2014'
import { hsscolP3062013 } from './21c-francis/hsscol-p306-2013'
import { hsscolP3072014 } from './21c-francis/hsscol-p307-2014'
import { hsscolP3092013 } from './21c-francis/hsscol-p309-2013'
import { hsscolP3102016 } from './21c-francis/hsscol-p310-2016'
import { hsscolP3112019 } from './21c-francis/hsscol-p311-2019'
import { hsscolP3122015 } from './21c-francis/hsscol-p312-2015'
import { hsscolP3132015 } from './21c-francis/hsscol-p313-2015'
import { hsscolP3152015 } from './21c-francis/hsscol-p315-2015'
import { hsscolP3172014 } from './21c-francis/hsscol-p317-2014'
import { hsscolP3182015 } from './21c-francis/hsscol-p318-2015'
import { hsscolP3202014 } from './21c-francis/hsscol-p320-2014'
import { hsscolP3212015 } from './21c-francis/hsscol-p321-2015'
import { hsscolP3222015 } from './21c-francis/hsscol-p322-2015'
import { hsscolP3232015 } from './21c-francis/hsscol-p323-2015'
import { hsscolP3242015 } from './21c-francis/hsscol-p324-2015'
import { hsscolP3262015 } from './21c-francis/hsscol-p326-2015'
import { hsscolP3272016 } from './21c-francis/hsscol-p327-2016'
import { hsscolP3282016 } from './21c-francis/hsscol-p328-2016'
import { hsscolP3362019 } from './21c-francis/hsscol-p336-2019'
import { vosEstisLuxMundi2019 } from './21c-francis/vos-estis-lux-mundi-2019'
import { hsscolP3892019 } from './21c-francis/hsscol-p389-2019'
import { hsscolP3902015 } from './21c-francis/hsscol-p390-2015'
import { hsscolP3922018 } from './21c-francis/hsscol-p392-2018'
import { hsscolP3982018 } from './21c-francis/hsscol-p398-2018'
import { hsscolP4002005 } from './21c-francis/hsscol-p400-2005'
import { hsscolP4012018 } from './21c-francis/hsscol-p401-2018'
import { hsscolP4022020 } from './21c-francis/hsscol-p402-2020'
import { hsscolP4032019 } from './21c-francis/hsscol-p403-2019'
import { hsscolP4042019 } from './21c-francis/hsscol-p404-2019'
import { hsscolP4052018 } from './21c-francis/hsscol-p405-2018'
import { hsscolP4062019 } from './21c-francis/hsscol-p406-2019'
import { hsscolP4072019 } from './21c-francis/hsscol-p407-2019'
import { hsscolP4082018 } from './21c-francis/hsscol-p408-2018'
import { hsscolP4092020 } from './21c-francis/hsscol-p409-2020'
import { hsscolP4102019 } from './21c-francis/hsscol-p410-2019'
import { hsscolP4112019 } from './21c-francis/hsscol-p411-2019'
import { hsscolP4122019 } from './21c-francis/hsscol-p412-2019'
import { hsscolP4132019 } from './21c-francis/hsscol-p413-2019'
import { hsscolP4142014 } from './21c-francis/hsscol-p414-2014'
import { hsscolP4152019 } from './21c-francis/hsscol-p415-2019'
import { hsscolP4162017 } from './21c-francis/hsscol-p416-2017'
import { hsscolP4172017 } from './21c-francis/hsscol-p417-2017'
import { hsscolP4182018 } from './21c-francis/hsscol-p418-2018'
import { hsscolP4192019 } from './21c-francis/hsscol-p419-2019'
import { hsscolP4202014 } from './21c-francis/hsscol-p420-2014'
import { hsscolP4212019 } from './21c-francis/hsscol-p421-2019'
import { hsscolP4222018 } from './21c-francis/hsscol-p422-2018'
import { hsscolP4232020 } from './21c-francis/hsscol-p423-2020'
import { hsscolP4242019 } from './21c-francis/hsscol-p424-2019'
import { hsscolP4322020 } from './21c-francis/hsscol-p432-2020'
import { hsscolP4332017 } from './21c-francis/hsscol-p433-2017'
import { hsscolP4342019 } from './21c-francis/hsscol-p434-2019'
import { hsscolP4352018 } from './21c-francis/hsscol-p435-2018'
import { hsscolP4362019 } from './21c-francis/hsscol-p436-2019'
import { hsscolP4372020 } from './21c-francis/hsscol-p437-2020'
import { hsscolP4382020 } from './21c-francis/hsscol-p438-2020'
import { hsscolP4422025 } from './21c-francis/hsscol-p442-2025'
import { hsscolP4432023 } from './21c-francis/hsscol-p443-2023'
import { hsscolP4442024 } from './21c-francis/hsscol-p444-2024'
import { patrisCorde2020 } from './21c-francis/patris-corde-2020'
import { hsscolP4462014 } from './21c-francis/hsscol-p446-2014'
import { hsscolP4472023 } from './21c-francis/hsscol-p447-2023'
import { hsscolP4492021 } from './21c-francis/hsscol-p449-2021'
import { hsscolP4502023 } from './21c-francis/hsscol-p450-2023'
import { patrisCorde2020Alt } from './21c-francis/patris-corde-2020-alt'
import { hsscolP4851962 } from './21c-francis/hsscol-p485-1962'
import { hsscolP4972025 } from './21c-francis/hsscol-p497-2025'
import { hsscolP5132018 } from './21c-francis/hsscol-p513-2018'
import { hsscolP5162024 } from './21c-francis/hsscol-p516-2024'
import { hsscolP5172023 } from './21c-francis/hsscol-p517-2023'
import { hsscolP5182022 } from './21c-francis/hsscol-p518-2022'
import { hsscolP5192013 } from './21c-francis/hsscol-p519-2013'
import { hsscolP5202023 } from './21c-francis/hsscol-p520-2023'
import { hsscolP5212022 } from './21c-francis/hsscol-p521-2022'
import { hsscolP5232022 } from './21c-francis/hsscol-p523-2022'
import { hsscolP5242022 } from './21c-francis/hsscol-p524-2022'
import { hsscolP5252021 } from './21c-francis/hsscol-p525-2021'
import { hsscolP5302021 } from './21c-francis/hsscol-p530-2021'
import { hsscolP5332025 } from './21c-francis/hsscol-p533-2025'
import { hsscolP5342025 } from './21c-francis/hsscol-p534-2025'
import { hsscolP5352025 } from './21c-francis/hsscol-p535-2025'
import { theHolySee2008 } from './21c-francis/the-holy-see-2008'
import { theHolySee2017 } from './21c-francis/the-holy-see-2017'
import { theHolySee2019 } from './21c-francis/the-holy-see-2019'



// ── 2026-05-28 hsscol BC 批次 — 20c-john-paul-ii ──
import { hsscolP3701991 } from './20c-john-paul-ii/hsscol-p370-1991'
import { hsscolP3722002 } from './20c-john-paul-ii/hsscol-p372-2002'
import { hsscolP3732001 } from './20c-john-paul-ii/hsscol-p373-2001'
import { hsscolP3752001 } from './20c-john-paul-ii/hsscol-p375-2001'
import { hsscolP3762001 } from './20c-john-paul-ii/hsscol-p376-2001'
import { hsscolP3771991 } from './20c-john-paul-ii/hsscol-p377-1991'
import { hsscolP3821991 } from './20c-john-paul-ii/hsscol-p382-1991'
import { hsscolP3911991 } from './20c-john-paul-ii/hsscol-p391-1991'

// ── 2026-05-28 hsscol BC 批次 — 20c-pius-xii ──
import { hsscolP1061955 } from './20c-pius-xii/hsscol-p106-1955'

// ── 2026-05-28 hsscol BC 批次 — 21c-benedict-xvi ──
import { hsscolP2632007 } from './21c-benedict-xvi/hsscol-p263-2007'
import { hsscolP3252009 } from './21c-benedict-xvi/hsscol-p325-2009'
import { hsscolP3332009 } from './21c-benedict-xvi/hsscol-p333-2009'
import { hsscolP3782009 } from './21c-benedict-xvi/hsscol-p378-2009'
import { hsscolP3792009 } from './21c-benedict-xvi/hsscol-p379-2009'
import { hsscolP3802009 } from './21c-benedict-xvi/hsscol-p380-2009'
import { hsscolP3812009 } from './21c-benedict-xvi/hsscol-p381-2009'
import { hsscolP3942009 } from './21c-benedict-xvi/hsscol-p394-2009'
import { hsscolP3952009 } from './21c-benedict-xvi/hsscol-p395-2009'

// ── 2026-05-28 hsscol BC 批次 — 21c-francis ──
import { hsscolP3112013 } from './21c-francis/hsscol-p311-2013'
import { hsscolP3302016 } from './21c-francis/hsscol-p330-2016'
import { hsscolP3392016 } from './21c-francis/hsscol-p339-2016'
import { hsscolP3962019 } from './21c-francis/hsscol-p396-2019'
import { hsscolP4291971 } from './21c-francis/hsscol-p429-1971'
import { hsscolP4822015 } from './21c-francis/hsscol-p482-2015'



// ── 2026-05-28 hsscol BC 批次 — 20c-john-paul-ii ──
import { hsscolP2162004 } from './20c-john-paul-ii/hsscol-p216-2004'
import { hsscolP3481994 } from './20c-john-paul-ii/hsscol-p348-1994'
import { hsscolP3742000 } from './20c-john-paul-ii/hsscol-p374-2000'
import { hsscolP4772001 } from './20c-john-paul-ii/hsscol-p477-2001'

// ── 2026-05-28 hsscol BC 批次 — 21c-benedict-xvi ──
import { hsscolP2832011 } from './21c-benedict-xvi/hsscol-p283-2011'

// ── 2026-05-28 hsscol BC 批次 — 21c-francis ──
import { hsscolP3492016 } from './21c-francis/hsscol-p349-2016'



// ── 2026-05-28 hsscol Haiku OCR — 21c-benedict-xvi ──
import { hsscolP2742009 } from './21c-benedict-xvi/hsscol-p274-2009'

// ── 2026-05-28 hsscol Haiku OCR — 21c-francis ──
import { hsscolP4512022 } from './21c-francis/hsscol-p451-2022'
import { hsscolP4522022 } from './21c-francis/hsscol-p452-2022'
import { hsscolP4532022 } from './21c-francis/hsscol-p453-2022'
import { hsscolP4542022 } from './21c-francis/hsscol-p454-2022'
import { hsscolP4552022 } from './21c-francis/hsscol-p455-2022'
import { hsscolP4562022 } from './21c-francis/hsscol-p456-2022'
import { hsscolP4572022 } from './21c-francis/hsscol-p457-2022'
import { hsscolP4652022 } from './21c-francis/hsscol-p465-2022'
import { hsscolP4662022 } from './21c-francis/hsscol-p466-2022'
import { hsscolP4672023 } from './21c-francis/hsscol-p467-2023'
import { hsscolP4682023 } from './21c-francis/hsscol-p468-2023'
import { hsscolP4692024 } from './21c-francis/hsscol-p469-2024'
import { hsscolP4702024 } from './21c-francis/hsscol-p470-2024'
import { hsscolP4712024 } from './21c-francis/hsscol-p471-2024'
import { hsscolP4722024 } from './21c-francis/hsscol-p472-2024'
import { hsscolP4732024 } from './21c-francis/hsscol-p473-2024'
import { hsscolP4742024 } from './21c-francis/hsscol-p474-2024'
import { hsscolP4752024 } from './21c-francis/hsscol-p475-2024'
import { hsscolP4762025 } from './21c-francis/hsscol-p476-2025'
import { hsscolP4782015 } from './21c-francis/hsscol-p478-2015'
import { hsscolP4802015 } from './21c-francis/hsscol-p480-2015'
import { hsscolP4812016 } from './21c-francis/hsscol-p481-2016'
import { hsscolP4832020 } from './21c-francis/hsscol-p483-2020'
import { hsscolP4862020 } from './21c-francis/hsscol-p486-2020'
import { hsscolP4882025 } from './21c-francis/hsscol-p488-2025'
import { hsscolP4892025 } from './21c-francis/hsscol-p489-2025'
import { hsscolP4902025 } from './21c-francis/hsscol-p490-2025'
import { hsscolP4912025 } from './21c-francis/hsscol-p491-2025'
import { hsscolP4922020 } from './21c-francis/hsscol-p492-2020'
import { hsscolP4932020 } from './21c-francis/hsscol-p493-2020'
import { hsscolP4942021 } from './21c-francis/hsscol-p494-2021'
import { hsscolP4952021 } from './21c-francis/hsscol-p495-2021'
import { hsscolP4962021 } from './21c-francis/hsscol-p496-2021'
import { hsscolP4982020 } from './21c-francis/hsscol-p498-2020'
import { hsscolP4992019 } from './21c-francis/hsscol-p499-2019'
import { hsscolP5002024 } from './21c-francis/hsscol-p500-2024'
import { hsscolP5012021 } from './21c-francis/hsscol-p501-2021'
import { hsscolP5022023 } from './21c-francis/hsscol-p502-2023'
import { hsscolP5032023 } from './21c-francis/hsscol-p503-2023'
import { hsscolP5042024 } from './21c-francis/hsscol-p504-2024'
import { hsscolP5052023 } from './21c-francis/hsscol-p505-2023'
import { hsscolP5062024 } from './21c-francis/hsscol-p506-2024'
import { hsscolP5072024 } from './21c-francis/hsscol-p507-2024'
import { hsscolP5082024 } from './21c-francis/hsscol-p508-2024'
import { hsscolP5092023 } from './21c-francis/hsscol-p509-2023'
import { hsscolP5102023 } from './21c-francis/hsscol-p510-2023'
import { hsscolP5112023 } from './21c-francis/hsscol-p511-2023'
import { hsscolP5122023 } from './21c-francis/hsscol-p512-2023'
import { hsscolP5152024 } from './21c-francis/hsscol-p515-2024'
import { hsscolP5222022 } from './21c-francis/hsscol-p522-2022'
import { hsscolP5262019 } from './21c-francis/hsscol-p526-2019'
import { hsscolP5272021 } from './21c-francis/hsscol-p527-2021'
import { hsscolP5282021 } from './21c-francis/hsscol-p528-2021'
import { hsscolP5292021 } from './21c-francis/hsscol-p529-2021'
import { hsscolP5312021 } from './21c-francis/hsscol-p531-2021'

// ── 2026-05-28 hsscol Haiku OCR — 21c-leo-xiv ──
import { hsscolP4872025 } from './21c-leo-xiv/hsscol-p487-2025'
import { hsscolP5382026 } from './21c-leo-xiv/hsscol-p538-2026'
import { hsscolP5392026 } from './21c-leo-xiv/hsscol-p539-2026'
import { hsscolP5402026 } from './21c-leo-xiv/hsscol-p540-2026'
import { hsscolP5412026 } from './21c-leo-xiv/hsscol-p541-2026'
import { hsscolP5422025 } from './21c-leo-xiv/hsscol-p542-2025'
import { hsscolP5432025 } from './21c-leo-xiv/hsscol-p543-2025'
import { hsscolP5442025 } from './21c-leo-xiv/hsscol-p544-2025'
import { hsscolP5452025 } from './21c-leo-xiv/hsscol-p545-2025'

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
  // Benedict XV
  adBeatissimiApostolorum1914,
  humaniGenerisRedemptionem1917,
  quodIamDiu1918,
  inHacTanta1919,
  paternoIamDiu1919,
  maximumIllud1919,
  pacemDeiMunusPulcherrimum1920,
  spiritusParaclitus1920,
  principiApostolorumPetro1920,
  annusIamPlenus1920,
  sacraPropediem1921,
  inPraeclaraSummorum1921,
  faustoAppetenteDie1921,
  // Pius X
  eSupremi1903,
  adDiemIllumLaetissimum1904,
  iucundaSane1904,
  acerboNimis1905,
  ilFermoProposito1905,
  vehementerNos1906,
  tribusCirciter1906,
  pieniLAnimo1906,
  gravissimoOfficiiMunere1906,
  uneFoisEncore1907,
  pascendiDominiciGregis1907,
  communiumRerum1909,
  editaeSaepe1910,
  iamdudum1911,
  lacrimabiliStatu1912,
  singulariQuadam1912,
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

  // ── 2026-05-28 B 區 (curia) ──
  dignitasInfinita2024,
  iuvenescitEcclesia2016,

  // ── 2026-05-28 hsscol — 20c-john-paul-ii ──
  catechesiTradendae1979,
  hsscolP1651979,
  hsscolP1682002,
  hsscolP1691981,
  familiarisConsortio1981,
  hsscolP1721983,
  reconciliatioEtPaenitentia1984,
  hsscolP1741984,
  hsscolP1751984,
  hsscolP1781987,
  hsscolP1791987,
  hsscolP1811988,
  hsscolP1821988,
  hsscolP1831988,
  redemptorisCustos1989,
  hsscolP1852002,
  pastoresDaboVobis1992,
  hsscolP1881993,
  ordinatioSacerdotalis1994,
  hsscolP1931995,
  hsscolP1941995,
  hsscolP1961995,
  hsscolP1971996,
  vitaConsecrata1996,
  hsscolP1991998,
  hsscolP2001998,
  hsscolP2011998,
  hsscolP2021998,
  adTuendamFidem1998,
  fideiDepositum1992,
  hsscolP2122001,
  hsscolP2132003,
  misericordiaDei2002,
  hsscolP2152004,
  hsscolP2171993,
  hsscolP2181999,
  hsscolP2192001,
  hsscolP2202004,
  hsscolP2232002,
  hsscolP2242005,
  hsscolP2252005,
  hsscolP2262005,
  hsscolP2302004,
  hsscolP2312004,
  hsscolP2322004,
  hsscolP2332004,
  hsscolP2341991,
  hsscolP2431994,
  hsscolP2442003,
  hsscolP2452002,
  hsscolP2462001,
  hsscolP2472005,
  hsscolP2492000,
  hsscolP2502001,
  hsscolP2512007,
  exCordeEcclesiae1990,
  hsscolP2702009,
  hsscolP2772010,
  hsscolP2992003,
  hsscolP3002003,
  hsscolP3451980,
  hsscolP3501982,
  hsscolP3531995,
  hsscolP3622002,
  hsscolP3632002,
  hsscolP3642002,
  hsscolP3652000,
  hsscolP3661999,
  hsscolP3672004,
  hsscolP3831999,
  hsscolP3841997,
  hsscolP3852003,
  hsscolP3862003,
  hsscolP3871997,
  theHolySee1994,

  // ── 2026-05-28 hsscol — 20c-paul-vi ──
  apostolicConstitutionOnTheFastAmpAbstinence1966,
  christianoGaudio1975,
  hsscolP0011967,
  hsscolP0031971,
  hsscolP0041970,
  hsscolP0051971,
  hsscolP0061971,
  hsscolP0071971,
  hsscolP0081971,
  hsscolP0091971,
  hsscolP0101971,
  hsscolP0111970,
  hsscolP0171967,
  hsscolP0181970,
  hsscolP0201967,
  hsscolP0221968,
  sacramLiturgiam1964,
  proCompertoSane1967,
  hsscolP0261969,
  studiaLatinitatis1964,
  hsscolP0401970,
  hsscolP0411970,
  hsscolP0421970,
  hsscolP0431970,
  hsscolP0441970,
  hsscolP0451970,
  hsscolP0461970,
  hsscolP0471970,
  hsscolP0561968,
  hsscolP0571969,
  hsscolP0581970,
  hsscolP0591970,
  hsscolP0601970,
  hsscolP0611970,
  hsscolP0621970,
  hsscolP0631970,
  hsscolP0641970,
  hsscolP0651970,
  hsscolP0721968,
  hsscolP1711983,
  hsscolP4581973,
  hsscolP4591970,
  regiminiEcclesiae1967,
  sacrarumIndulgentiarumRecognitio1967,
  sacrumDiaconatus1967,

  // ── 2026-05-28 hsscol — 20c-pius-xi ──
  deAcrisMissionibusProvehendis1926,
  diviniMagistri1929,
  hsscolP0761931,
  hsscolP0771935,
  hsscolP0781922,
  hsscolP0801926,

  // ── 2026-05-28 hsscol — 20c-pius-xii ──
  hsscolP0941939,
  hsscolP0951940,
  hsscolP0961940,
  hsscolP0971940,
  hsscolP0981940,
  hsscolP1001941,
  hsscolP1041943,
  hsscolP1051951,
  hsscolP1071943,
  hsscolP1081943,
  hsscolP1091944,
  hsscolP1101944,
  hsscolP1111945,
  hsscolP1121945,
  hsscolP1131945,
  hsscolP1141946,
  hsscolP1151946,
  hsscolP1171947,
  hsscolP1181947,
  hsscolP1191948,
  hsscolP1201949,
  hsscolP1211949,
  hsscolP1221951,
  hsscolP1231951,
  hsscolP1241956,
  hsscolP1251956,
  hsscolP1261958,
  hsscolP1271949,
  hsscolP1281950,
  hsscolP1292002,
  hsscolP1301951,
  hsscolP1321952,
  hsscolP1331952,
  hsscolP1342002,
  christusDominus1953,
  cupimusImprimis1952,
  hsscolP1381953,
  hsscolP1391953,
  hsscolP1401953,
  hsscolP1411954,
  sacraVirginitas1954,
  hsscolP1431954,
  hsscolP1461955,
  hsscolP1471955,
  hsscolP1481955,
  hsscolP1491955,
  hsscolP1501956,
  hsscolP1541957,
  hsscolP1551957,
  hsscolP1561957,
  hsscolP1571957,
  hsscolP1581957,
  hsscolP1591957,
  mirandaProrsus1957,
  hsscolP1611958,
  hsscolP1621958,
  hsscolP2061955,
  hsscolP2071956,
  hsscolP2081957,
  hsscolP2091958,
  laSolennita1941,
  votreVisite1956,

  // ── 2026-05-28 hsscol — 21c-benedict-xvi ──
  hsscolP2272006,
  hsscolP2282006,
  hsscolP2292006,
  hsscolP2392006,
  hsscolP2402005,
  hsscolP2412007,
  hsscolP2422007,
  hsscolP2482006,
  hsscolP2602005,
  hsscolP2612007,
  hsscolP2622005,
  hsscolP2642006,
  hsscolP2652008,
  hsscolP2661970,
  hsscolP2672009,
  hsscolP2682009,
  hsscolP2692006,
  hsscolP2712005,
  hsscolP2722006,
  hsscolP2732009,
  hsscolP2752010,
  hsscolP2762010,
  hsscolP2782009,
  hsscolP2792011,
  hsscolP2802011,
  hsscolP2812010,
  hsscolP2822011,
  hsscolP2842011,
  hsscolP2852011,
  hsscolP2862011,
  hsscolP2872010,
  hsscolP2882012,
  hsscolP2892012,
  hsscolP2902012,
  hsscolP2912012,
  hsscolP2922012,
  hsscolP2932012,
  hsscolP2942012,
  hsscolP2952011,
  hsscolP2962013,
  hsscolP2972012,
  hsscolP2982013,
  hsscolP3012013,
  hsscolP3052013,
  hsscolP3142007,
  hsscolP3192013,
  hsscolP4792009,

  // ── 2026-05-28 hsscol — 21c-francis ──
  chineseRegionalBishops2017,
  hsscolP3032014,
  hsscolP3042014,
  hsscolP3062013,
  hsscolP3072014,
  hsscolP3092013,
  hsscolP3102016,
  hsscolP3112019,
  hsscolP3122015,
  hsscolP3132015,
  hsscolP3152015,
  hsscolP3172014,
  hsscolP3182015,
  hsscolP3202014,
  hsscolP3212015,
  hsscolP3222015,
  hsscolP3232015,
  hsscolP3242015,
  hsscolP3262015,
  hsscolP3272016,
  hsscolP3282016,
  hsscolP3362019,
  vosEstisLuxMundi2019,
  hsscolP3892019,
  hsscolP3902015,
  hsscolP3922018,
  hsscolP3982018,
  hsscolP4002005,
  hsscolP4012018,
  hsscolP4022020,
  hsscolP4032019,
  hsscolP4042019,
  hsscolP4052018,
  hsscolP4062019,
  hsscolP4072019,
  hsscolP4082018,
  hsscolP4092020,
  hsscolP4102019,
  hsscolP4112019,
  hsscolP4122019,
  hsscolP4132019,
  hsscolP4142014,
  hsscolP4152019,
  hsscolP4162017,
  hsscolP4172017,
  hsscolP4182018,
  hsscolP4192019,
  hsscolP4202014,
  hsscolP4212019,
  hsscolP4222018,
  hsscolP4232020,
  hsscolP4242019,
  hsscolP4322020,
  hsscolP4332017,
  hsscolP4342019,
  hsscolP4352018,
  hsscolP4362019,
  hsscolP4372020,
  hsscolP4382020,
  hsscolP4422025,
  hsscolP4432023,
  hsscolP4442024,
  patrisCorde2020,
  hsscolP4462014,
  hsscolP4472023,
  hsscolP4492021,
  hsscolP4502023,
  patrisCorde2020Alt,
  hsscolP4851962,
  hsscolP4972025,
  hsscolP5132018,
  hsscolP5162024,
  hsscolP5172023,
  hsscolP5182022,
  hsscolP5192013,
  hsscolP5202023,
  hsscolP5212022,
  hsscolP5232022,
  hsscolP5242022,
  hsscolP5252021,
  hsscolP5302021,
  hsscolP5332025,
  hsscolP5342025,
  hsscolP5352025,
  theHolySee2008,
  theHolySee2017,
  theHolySee2019,


  // ── 2026-05-28 hsscol — 20c-john-paul-ii ──
  hsscolP3701991,
  hsscolP3722002,
  hsscolP3732001,
  hsscolP3752001,
  hsscolP3762001,
  hsscolP3771991,
  hsscolP3821991,
  hsscolP3911991,

  // ── 2026-05-28 hsscol — 20c-pius-xii ──
  hsscolP1061955,

  // ── 2026-05-28 hsscol — 21c-benedict-xvi ──
  hsscolP2632007,
  hsscolP3252009,
  hsscolP3332009,
  hsscolP3782009,
  hsscolP3792009,
  hsscolP3802009,
  hsscolP3812009,
  hsscolP3942009,
  hsscolP3952009,

  // ── 2026-05-28 hsscol — 21c-francis ──
  hsscolP3112013,
  hsscolP3302016,
  hsscolP3392016,
  hsscolP3962019,
  hsscolP4291971,
  hsscolP4822015,


  // ── 2026-05-28 hsscol — 20c-john-paul-ii ──
  hsscolP2162004,
  hsscolP3481994,
  hsscolP3742000,
  hsscolP4772001,

  // ── 2026-05-28 hsscol — 21c-benedict-xvi ──
  hsscolP2832011,

  // ── 2026-05-28 hsscol — 21c-francis ──
  hsscolP3492016,


  // ── 2026-05-28 hsscol Haiku — 21c-benedict-xvi ──
  hsscolP2742009,

  // ── 2026-05-28 hsscol Haiku — 21c-francis ──
  hsscolP4512022,
  hsscolP4522022,
  hsscolP4532022,
  hsscolP4542022,
  hsscolP4552022,
  hsscolP4562022,
  hsscolP4572022,
  hsscolP4652022,
  hsscolP4662022,
  hsscolP4672023,
  hsscolP4682023,
  hsscolP4692024,
  hsscolP4702024,
  hsscolP4712024,
  hsscolP4722024,
  hsscolP4732024,
  hsscolP4742024,
  hsscolP4752024,
  hsscolP4762025,
  hsscolP4782015,
  hsscolP4802015,
  hsscolP4812016,
  hsscolP4832020,
  hsscolP4862020,
  hsscolP4882025,
  hsscolP4892025,
  hsscolP4902025,
  hsscolP4912025,
  hsscolP4922020,
  hsscolP4932020,
  hsscolP4942021,
  hsscolP4952021,
  hsscolP4962021,
  hsscolP4982020,
  hsscolP4992019,
  hsscolP5002024,
  hsscolP5012021,
  hsscolP5022023,
  hsscolP5032023,
  hsscolP5042024,
  hsscolP5052023,
  hsscolP5062024,
  hsscolP5072024,
  hsscolP5082024,
  hsscolP5092023,
  hsscolP5102023,
  hsscolP5112023,
  hsscolP5122023,
  hsscolP5152024,
  hsscolP5222022,
  hsscolP5262019,
  hsscolP5272021,
  hsscolP5282021,
  hsscolP5292021,
  hsscolP5312021,

  // ── 2026-05-28 hsscol Haiku — 21c-leo-xiv ──
  hsscolP4872025,
  hsscolP5382026,
  hsscolP5392026,
  hsscolP5402026,
  hsscolP5412026,
  hsscolP5422025,
  hsscolP5432025,
  hsscolP5442025,
  hsscolP5452025,

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
