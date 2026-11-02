# -*- coding: utf-8 -*-
"""Bangun 'Ilmu Lughah 3 (Latihan Bab 8-11).html' memakai template ujian Tarikh Al Adab 5.
Soal: (bab, pertanyaan, jawaban benar, jawaban salah, penjelasan). Posisi jawaban diacak tetap (seed)."""
import json, os, random, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
S5 = os.path.join(ROOT, 'Data', 'Data Lughoh per Semester', 'Semester 5')
TPL = os.path.join(S5, 'تاريخ الأدب العربي (5)', 'Muqarrar Tarikh Al Adab Al Arabi 5 (Latihan Bab 1-4).html')
OUT = os.path.join(S5, 'علم اللغة (3)', 'Ilmu Lughah 3 (Latihan Bab 8-11).html')

BAB = {'8': 'Pembagian Bunyi menurut Makhraj', '9': 'Sifat-Sifat Bunyi', '10': 'Suku Kata (Silabel)', '11': 'Performa Vokal'}
BMAP = {1: 8, 2: 9, 4: 10, 3: 11}   # nomor bab di halaman materi

Q = []
def q(b, t, ok, no, e): Q.append((b, t, ok, no, e))

# ---------------- Bab 1: makhraj
q(1, 'كَمْ عَدَدُ أَصْوَاتِ اللُّغَةِ الْعَرَبِيَّةِ؟', 'أَرْبَعَةٌ وَثَلَاثُونَ صَوْتًا', 'ثَمَانِيَةٌ وَعِشْرُونَ صَوْتًا', 'Bahasa Arab memiliki 34 bunyi: 28 konsonan dan 6 vokal.')
q(1, 'كَمْ عَدَدُ الْأَصْوَاتِ الصَّامِتَةِ فِي الْعَرَبِيَّةِ؟', 'ثَمَانِيَةٌ وَعِشْرُونَ صَوْتًا', 'سِتَّةُ أَصْوَاتٍ', 'Bunyi konsonan (shamitah) berjumlah 28, mewakili huruf hijaiyah.')
q(1, 'كَمْ عَدَدُ الْأَصْوَاتِ الصَّائِتَةِ (الْحَرَكَاتِ)؟', 'سِتَّةُ أَصْوَاتٍ', 'ثَلَاثَةُ أَصْوَاتٍ', 'Vokal berjumlah enam: fathah, dhammah, kasrah masing-masing pendek dan panjang.')
q(1, 'مَا مَخْرَجُ الْحَرْفِ؟', 'مَوْضِعُ خُرُوجِ الْحَرْفِ', 'كَيْفِيَّةٌ يُوصَفُ بِهَا الْحَرْفُ', 'Makhraj adalah tempat keluarnya huruf; adapun cara/keadaan disebut sifat.')
q(1, 'كَيْفَ نُحَدِّدُ مَخْرَجَ الْحَرْفِ؟', 'بِالنُّطْقِ بِهِ سَاكِنًا بَعْدَ هَمْزَةٍ', 'بِالنُّطْقِ بِهِ مُتَحَرِّكًا فِي أَوَّلِ الْكَلَامِ', 'Huruf diucapkan sukun (atau bertasydid) setelah hamzah, lalu didengar di mana suaranya terputus.')
q(1, 'مَنِ الْقَائِلُونَ بِأَنَّ مَخَارِجَ الْحُرُوفِ سَبْعَةَ عَشَرَ؟', 'الْخَلِيلُ وَمَكِّيٌّ وَتَبِعَهُمَا ابْنُ الْجَزَرِيِّ', 'الْفَرَّاءُ وَالْجَرْمِيُّ وَقُطْرُبٌ', 'Pendapat 17 makhraj: Al-Khalil, Makki bin Abi Thalib, lalu diikuti Ibnu Al-Jazari.')
q(1, 'مَنِ الْقَائِلُونَ بِأَنَّ مَخَارِجَ الْحُرُوفِ أَرْبَعَةَ عَشَرَ؟', 'الْفَرَّاءُ وَالْجَرْمِيُّ وَقُطْرُبٌ وَابْنُ كَيْسَانَ', 'سِيبَوَيْهِ وَالشَّاطِبِيُّ', 'Pendapat 14 makhraj: Al-Farra\', Al-Jarmi, Quthrub, dan Ibnu Kaisan.')
q(1, 'مَنِ الْقَائِلُ بِأَنَّ الْمَخَارِجَ سِتَّةَ عَشَرَ؟', 'سِيبَوَيْهِ وَتَبِعَهُ الشَّاطِبِيُّ', 'الْخَلِيلُ بْنُ أَحْمَدَ', 'Pendapat 16 makhraj: Sibawaih, diikuti Asy-Syathibi.')
q(1, 'كَمْ مَخْرَجًا لِلْأَصْوَاتِ فِي الْقَوْلِ الَّذِي اعْتُمِدَ فِي هَذَا الْمُقَرَّرِ؟', 'سَبْعَةَ عَشَرَ مَخْرَجًا', 'أَرْبَعَةَ عَشَرَ مَخْرَجًا', 'Dari uraian disimpulkan jumlah makhraj bunyi adalah tujuh belas.')
q(1, 'مَا الْحَرْفَانِ الْخَارِجَانِ مِنْ أَقْصَى الْحَلْقِ؟', 'الْهَمْزَةُ وَالْهَاءُ', 'الْعَيْنُ وَالْحَاءُ', 'Pangkal tekak: hamzah dan ha.')
q(1, 'مَا الْحَرْفَانِ الْخَارِجَانِ مِنْ وَسَطِ الْحَلْقِ؟', 'الْعَيْنُ وَالْحَاءُ', 'الْغَيْنُ وَالْخَاءُ', 'Tengah tekak: \'ain dan ha.')
q(1, 'مَا الْحَرْفَانِ الْخَارِجَانِ مِنْ أَدْنَى الْحَلْقِ؟', 'الْغَيْنُ وَالْخَاءُ', 'الْهَمْزَةُ وَالْهَاءُ', 'Ujung tekak (terdekat ke mulut): ghain dan kha.')
q(1, 'كَمْ عَدَدُ الْأَصْوَاتِ الْحَلْقِيَّةِ؟', 'سِتَّةُ أَصْوَاتٍ', 'ثَلَاثَةُ أَصْوَاتٍ', 'Dua dari tiap bagian tekak, sehingga enam: hamzah, ha, kha, \'ain, ghain, ha.')
q(1, 'مِنْ أَيْنَ يَخْرُجُ صَوْتُ الْقَافِ؟', 'مِنْ أَقْصَى اللِّسَانِ', 'مِنْ وَسَطِ اللِّسَانِ', 'Qaf keluar dari pangkal lidah yang paling dekat dengan tekak; kaf sedikit di depannya.')
q(1, 'مَا الْأَصْوَاتُ الْخَارِجَةُ مِنْ وَسَطِ اللِّسَانِ؟', 'الْجِيمُ وَالشِّينُ وَالْيَاءُ', 'الْقَافُ وَالْكَافُ', 'Tengah lidah: jim, syin, dan ya.')
q(1, 'مِنْ أَيْنَ يَخْرُجُ صَوْتُ الضَّادِ؟', 'مِنْ حَافَّةِ اللِّسَانِ مَعَ الْأَضْرَاسِ الْعُلْيَا', 'مِنْ طَرَفِ اللِّسَانِ مَعَ أُصُولِ الثَّنَايَا', 'Dhad keluar dari tepi lidah dengan gigi geraham atas yang sejajar.')
q(1, 'مِنْ أَيْنَ يَخْرُجُ صَوْتُ النُّونِ؟', 'طَرَفُ اللِّسَانِ مَعَ لِثَةِ الْأَسْنَانِ الْعُلْيَا', 'بَيْنَ الشَّفَتَيْنِ', 'Nun: ujung lidah dengan gusi gigi atas yang berhadapan dengannya.')
q(1, 'مَا الْأَصْوَاتُ الْخَارِجَةُ مِنْ طَرَفِ اللِّسَانِ مَعَ أُصُولِ الثَّنَايَا الْعُلْيَا؟', 'الطَّاءُ وَالتَّاءُ وَالدَّالُ', 'السِّينُ وَالصَّادُ وَالزَّايُ', 'Ujung lidah dengan pangkal gigi seri atas: tha, ta, dan dal.')
q(1, 'مَا الْأَصْوَاتُ الْخَارِجَةُ مِنْ طَرَفِ اللِّسَانِ وَفَوْقَ الثَّنَايَا السُّفْلَى؟', 'السِّينُ وَالصَّادُ وَالزَّايُ', 'الذَّالُ وَالثَّاءُ وَالظَّاءُ', 'Ujung lidah di atas gigi seri bawah: sin, shad, dan za.')
q(1, 'مَا الْأَصْوَاتُ الْخَارِجَةُ مِنْ طَرَفِ اللِّسَانِ وَأَطْرَافِ الثَّنَايَا الْعُلْيَا؟', 'الذَّالُ وَالثَّاءُ وَالظَّاءُ', 'الطَّاءُ وَالتَّاءُ وَالدَّالُ', 'Ujung lidah dengan ujung gigi seri atas: dzal, tsa, dan zha.')
q(1, 'كَمْ عَدَدُ الْأَصْوَاتِ الَّتِي تَخْرُجُ مِنَ اللِّسَانِ؟', 'ثَمَانِيَةَ عَشَرَ صَوْتًا', 'ثَلَاثَةُ أَصْوَاتٍ', 'Dari lidah keluar delapan belas bunyi.')
q(1, 'مَا الْأَصْوَاتُ الْخَارِجَةُ مِنْ بَيْنِ الشَّفَتَيْنِ؟', 'الْبَاءُ وَالْمِيمُ وَالْوَاوُ', 'الْفَاءُ وَالْقَافُ وَالْكَافُ', 'Antara dua bibir: ba, mim, dan wau (wau tanpa merapatnya bibir).')
q(1, 'مَا الصَّوْتُ الْخَارِجُ مِنَ الشَّفَةِ السُّفْلَى مَعَ رُؤُوسِ الثَّنَايَا الْعُلْيَا؟', 'الْفَاءُ', 'الْبَاءُ', 'Fa keluar dari menempelnya bibir bawah pada ujung gigi seri atas.')
q(1, 'مَاذَا يَخْرُجُ مِنَ الْجَوْفِ؟', 'حُرُوفُ الْمَدِّ', 'الْغُنَّةُ', 'Al-jauf: satu makhraj untuk tiga huruf mad (vokal panjang).')
q(1, 'مَاذَا يَخْرُجُ مِنَ الْخَيْشُومِ؟', 'الْغُنَّةُ', 'حُرُوفُ الْمَدِّ', 'Khaisyum (hidung): ghunnah, yang menyertai mim dan nun.')

# ---------------- Bab 2: sifat
q(2, 'كَمْ عَدَدُ صِفَاتِ الْأَصْوَاتِ عِنْدَ الْمُجَوِّدِينَ عَلَى الْقَوْلِ الْمُخْتَارِ؟', 'سَبْعَ عَشْرَةَ صِفَةً', 'خَمْسَ عَشْرَةَ صِفَةً', 'Jumlah sifat menurut pendapat yang dipilih ahli tajwid adalah tujuh belas.')
q(2, 'مَا صِفَةُ الْحَرْفِ؟', 'كَيْفِيَّةٌ يُوصَفُ بِهَا الْحَرْفُ عِنْدَ حُصُولِهِ فِي الْمَخْرَجِ', 'الْمَوْضِعُ الَّذِي يَخْرُجُ مِنْهُ الْحَرْفُ', 'Sifat adalah keadaan yang menjadi ciri huruf ketika terbentuk di makhrajnya.')
q(2, 'مَا الْجَهْرُ؟', 'مَنْعُ جَرَيَانِ النَّفَسِ عِنْدَ النُّطْقِ بِالْحَرْفِ لِقُوَّةِ الِاعْتِمَادِ عَلَيْهِ', 'جَرَيَانُ النَّفَسِ مَعَ الْحَرْفِ لِضَعْفِ الِاعْتِمَادِ عَلَيْهِ', 'Jahr: napas tertahan karena kuatnya tumpuan di makhraj; termasuk sifat kekuatan.')
q(2, 'مَا ضِدُّ الْجَهْرِ؟', 'الْهَمْسُ', 'الشِّدَّةُ', 'Lawan jahr adalah hams, sifat kelemahan.')
q(2, 'كَمْ عَدَدُ حُرُوفِ الْهَمْسِ؟', 'عَشَرَةٌ', 'ثَمَانِيَةٌ', 'Huruf hams ada sepuluh; sisanya huruf jahr.')
q(2, 'مَا الْعِبَارَةُ الْجَامِعَةُ لِحُرُوفِ الْهَمْسِ؟', 'فَحَثَّهُ شَخْصٌ سَكَتَ', 'أَجِدْ قَطٍّ بَكَتْ', '«Fa ḥatstsahu syakhshun sakata» menghimpun huruf hams.')
q(2, 'كَمْ عَدَدُ حُرُوفِ الشِّدَّةِ؟', 'ثَمَانِيَةٌ', 'خَمْسَةٌ', 'Huruf syiddah ada delapan.')
q(2, 'مَا الْعِبَارَةُ الْجَامِعَةُ لِحُرُوفِ الشِّدَّةِ؟', 'أَجِدْ قَطٍّ بَكَتْ', 'لِنْ عُمَرَ', '«Ajid qaththin bakat» menghimpun huruf syiddah.')
q(2, 'كَمْ عَدَدُ حُرُوفِ التَّوَسُّطِ وَمَا جَامِعُهَا؟', 'خَمْسَةٌ، وَجَامِعُهَا: لِنْ عُمَرَ', 'ثَمَانِيَةٌ، وَجَامِعُهَا: أَجِدْ قَطٍّ بَكَتْ', 'Tawassuth ada lima huruf: lam, nun, \'ain, mim, ra («lin \'Umar»).')
q(2, 'مَا الرَّخَاوَةُ؟', 'جَرَيَانُ الصَّوْتِ مَعَ الْحَرْفِ لِضَعْفِهِ فِي الْمَخْرَجِ', 'امْتِنَاعُ جَرَيَانِ الصَّوْتِ مَعَ الْحَرْفِ', 'Rakhawah (frikatif): bunyi mengalir karena lemahnya tumpuan; huruf sisa selain syiddah dan tawassuth.')
q(2, 'كَمْ عَدَدُ حُرُوفِ الِاسْتِعْلَاءِ؟', 'سَبْعَةٌ', 'أَرْبَعَةٌ', 'Huruf isti\'la ada tujuh.')
q(2, 'مَا حُرُوفُ الِاسْتِعْلَاءِ؟', 'الْخَاءُ وَالصَّادُ وَالضَّادُ وَالْغَيْنُ وَالطَّاءُ وَالْقَافُ وَالظَّاءُ', 'الْفَاءُ وَالرَّاءُ وَالْمِيمُ وَالنُّونُ وَاللَّامُ وَالْبَاءُ', 'Huruf isti\'la (tafkhim): kha, shad, dhad, ghain, tha, qaf, zha.')
q(2, 'أَيُّ حُرُوفِ الِاسْتِعْلَاءِ أَقْوَاهَا؟', 'الظَّاءُ', 'الْقَافُ', 'Yang paling kuat di antara huruf isti\'la adalah zha.')
q(2, 'مَا الِاسْتِفَالُ؟', 'انْخِفَاضُ اللِّسَانِ عَنِ الْحَنَكِ الْأَعْلَى عِنْدَ النُّطْقِ بِالْحَرْفِ', 'ارْتِفَاعُ اللِّسَانِ إِلَى الْحَنَكِ الْأَعْلَى', 'Istifal adalah lawan isti\'la: lidah turun dari langit-langit atas.')
q(2, 'كَمْ عَدَدُ حُرُوفِ الْإِطْبَاقِ؟', 'أَرْبَعَةٌ', 'سَبْعَةٌ', 'Huruf ithbaq ada empat.')
q(2, 'مَا حُرُوفُ الْإِطْبَاقِ؟', 'الصَّادُ وَالضَّادُ وَالطَّاءُ وَالظَّاءُ', 'الْخَاءُ وَالْغَيْنُ وَالْقَافُ وَالطَّاءُ', 'Ithbaq: shad, dhad, tha, zha; keempatnya huruf tafkhim yang paling kuat.')
q(2, 'كَمْ عَدَدُ حُرُوفِ الِانْفِتَاحِ؟', 'خَمْسَةٌ وَعِشْرُونَ', 'أَرْبَعَةٌ', 'Infitah: semua huruf selain huruf ithbaq, yaitu dua puluh lima.')
q(2, 'كَمْ عَدَدُ حُرُوفِ الْإِذْلَاقِ وَمَا جَامِعُهَا؟', 'سِتَّةٌ، وَجَامِعُهَا: فَرَّ مِنْ لُبٍّ', 'خَمْسَةٌ، وَجَامِعُهَا: قُطْبُ جَدٍّ', 'Idzlaq ada enam huruf: fa, ra, mim, nun, lam, ba («farra min lubbin»).')
q(2, 'مَا حُرُوفُ الصَّفِيرِ؟', 'الصَّادُ وَالزَّايُ وَالسِّينُ', 'الشِّينُ وَالْجِيمُ وَالْيَاءُ', 'Shafir: shad, za, sin; yang terkuat adalah shad.')
q(2, 'كَمْ عَدَدُ حُرُوفِ الْقَلْقَلَةِ وَمَا جَامِعُهَا؟', 'خَمْسَةٌ، وَجَامِعُهَا: قُطْبُ جَدٍّ', 'سِتَّةٌ، وَجَامِعُهَا: فَرَّ مِنْ لُبٍّ', 'Qalqalah ada lima huruf: qaf, tha, ba, jim, dal («quthbu jaddin»).')
q(2, 'فِي أَيِّ حَرْفٍ تَكُونُ الْقَلْقَلَةُ فِي أَعْلَى مَرَاتِبِهَا؟', 'الطَّاءُ', 'الدَّالُ', 'Qalqalah tertinggi pada tha, menengah pada jim, terendah pada huruf lainnya.')
q(2, 'مَا حَرْفَا اللِّينِ؟', 'الْوَاوُ وَالْيَاءُ السَّاكِنَتَانِ الْمَفْتُوحُ مَا قَبْلَهُمَا', 'الْأَلِفُ وَالْهَمْزَةُ', 'Layn: wau dan ya sukun yang huruf sebelumnya berfathah, seperti «khaufun».')
q(2, 'مَا حَرْفَا الِانْحِرَافِ؟', 'اللَّامُ وَالرَّاءُ', 'النُّونُ وَالْمِيمُ', 'Inhiraf: lam dan ra, karena menyimpang dari makhrajnya.')
q(2, 'مَا الصِّفَةُ الْخَاصَّةُ بِالرَّاءِ، وَهِيَ ارْتِعَادُ رَأْسِ اللِّسَانِ؟', 'التَّكْرِيرُ', 'التَّفَشِّي', 'Takrir adalah getaran ujung lidah, khusus ra; diberi sedikit saja agar tidak hilang.')
q(2, 'التَّفَشِّي صِفَةٌ خَاصَّةٌ بِأَيِّ حَرْفٍ؟', 'الشِّينِ', 'الضَّادِ', 'Tafasysyi: tersebarnya udara saat mengucapkan syin.')
q(2, 'الِاسْتِطَالَةُ صِفَةٌ خَاصَّةٌ بِأَيِّ حَرْفٍ؟', 'الضَّادِ', 'الشِّينِ', 'Istithalah: terbentangnya bunyi dari awal tepi lidah hingga akhirnya; khusus dhad.')

# ---------------- Bab 3: performa vokal
q(3, 'مَا الْأَدَاءُ الصَّوْتِيُّ؟', 'فَنُّ اسْتِخْدَامِ الصَّوْتِ لِلتَّعْبِيرِ عَنِ الْمَعَانِي وَإِيصَالِ الْمَشَاعِرِ', 'دِرَاسَةُ مَخَارِجِ الْحُرُوفِ فَقَطْ', 'Performa vokal adalah seni menggunakan suara untuk mengungkapkan makna dan perasaan.')
q(3, 'هَلِ الْأَدَاءُ الصَّوْتِيُّ مُجَرَّدُ صَوْتٍ جَمِيلٍ؟', 'لَا، بَلْ مَهَارَةٌ تَتَطَلَّبُ فَهْمًا عَمِيقًا لِلنَّصِّ', 'نَعَمْ، يَكْفِي حُسْنُ الصَّوْتِ', 'Ia bukan sekadar suara merdu, melainkan keterampilan yang menuntut pemahaman teks.')
q(3, 'أَيُّ هَذِهِ مِنْ تِقْنِيَّاتِ الْأَدَاءِ الصَّوْتِيِّ؟', 'التَّنْغِيمُ وَالْوَقَفَاتُ وَالتَّحَكُّمُ فِي الطَّبَقَاتِ الصَّوْتِيَّةِ', 'الْإِدْغَامُ وَالْإِبْدَالُ وَالْإِعْلَالُ', 'Teknik khususnya: intonasi, jeda, dan pengendalian register suara.')
q(3, 'مَا الْبَرَامِجُ الْوَثَائِقِيَّةُ؟', 'بَرَامِجُ تُوَثِّقُ الْحَقَائِقَ الْحَيَاتِيَّةَ بِصُورَةٍ حِيَادِيَّةٍ', 'إِعْلَانَاتٌ تِجَارِيَّةٌ لِلتَّسْوِيقِ', 'Program dokumenter mendokumentasikan fakta kehidupan secara netral.')
q(3, 'مَا الْكُتُبُ السَّمْعِيَّةُ؟', 'نُسَخٌ صَوْتِيَّةٌ نَاطِقَةٌ مِنْ كِتَابٍ أَوْ مَجَلَّةٍ أَوْ نَصٍّ مَكْتُوبٍ', 'رُسُومٌ مُتَحَرِّكَةٌ لِلْأَطْفَالِ', 'Buku audio: versi suara dari buku, majalah, atau teks tertulis.')
q(3, 'مَا الْبَلَاغَاتُ؟', 'أَدَوَاتٌ صَوْتِيَّةٌ إِرْشَادِيَّةٌ فِي الْمَطَارَاتِ وَمُحِيطَاتِ الْقِطَارِ', 'بَرَامِجُ الرُّسُومِ الْمُتَحَرِّكَةِ', 'Pengumuman publik: sarana suara pemandu di bandara, stasiun, dan tempat umum.')
q(3, 'مَا إِعْلَانَاتُ الْخِدْمَةِ الْعَامَّةِ؟', 'إِعْلَانَاتٌ غَيْرُ رِبْحِيَّةٍ غَرَضُهَا تَوْعِيَةُ الْجُمْهُورِ', 'إِعْلَانَاتٌ رِبْحِيَّةٌ لِبَيْعِ السِّلَعِ', 'Iklan layanan masyarakat bersifat nonprofit untuk mengedukasi publik.')
q(3, 'مَا الَّذِي يُلْحَقُ بِالدَّبْلَجَةِ؟', 'إِعَادَةُ تَسْجِيلِ الْحِوَارِ وَالْمُؤَثِّرَاتِ الْبَشَرِيَّةِ اللَّفْظِيَّةِ', 'كِتَابَةُ النَّصِّ وَتَنْقِيطُهُ', 'Dubbing meliputi perekaman ulang dialog dan efek suara manusia secara verbal.')
q(3, 'مَا التَّرْجَمَةُ النَّاطِقَةُ؟', 'نَقْلُ كَلَامِ الْمُتَحَدِّثِ إِلَى لُغَةٍ أُخْرَى', 'كِتَابَةُ كَلَامِ الْمُتَحَدِّثِ بِحُرُوفٍ أُخْرَى', 'Sulih suara terjemahan: mengalihkan ujaran pembicara ke bahasa lain.')
q(3, 'مَا الَّذِي تَتَضَمَّنُهُ بَرَامِجُ الشَّخْصِيَّةِ الْمُتَحَرِّكَةِ؟', 'الرُّسُومُ الْمُتَحَرِّكَةُ وَاللُّعَبُ النَّاطِقَةُ وَأَلْعَابُ الْفِيدْيُو', 'الْبَلَاغَاتُ وَالنَّشَرَاتُ الْإِخْبَارِيَّةُ', 'Program karakter animasi: animasi, mainan bersuara, dan video game.')
q(3, 'أَيُّ هَذِهِ مِنَ الِاتِّصَالَاتِ الْهَاتِفِيَّةِ؟', 'الْبَرِيدُ الصَّوْتِيُّ وَالرَّدُّ الصَّوْتِيُّ التَّفَاعُلِيُّ', 'الْكُتُبُ السَّمْعِيَّةُ', 'Komunikasi telepon: voicemail, IVR, menu pengarahan panggilan.')
q(3, 'مَا تَحْلِيلُ النَّصِّ؟', 'سَبِيلُ الْمُؤَدِّي الصَّوْتِيِّ لِفَهْمِ مَاهِيَّةِ النَّصِّ وَتَفْسِيرِهِ', 'خَارِطَةُ الطَّرِيقِ لِلْإِرْشَادِ الْبَصَرِيِّ', 'Analisis teks adalah jalan memahami hakikat teks dan menafsirkannya.')
q(3, 'مَا التَّأْشِيرُ؟', 'خَارِطَةُ الطَّرِيقِ لِلْإِرْشَادِ الْبَصَرِيِّ خِلَالَ النَّصِّ', 'إِتْقَانُ قَوَاعِدِ اللُّغَةِ', 'Penandaan (marking): peta jalan visual sepanjang teks, sesuai keinginan pengisi suara.')
q(3, 'مَا الْمَقْصُودُ بِإِجَادَةِ اللُّغَةِ؟', 'إِتْقَانُ اللُّغَةِ السَّلِيمَةِ وَقَوَاعِدِهَا لِضَمَانِ الِاحْتِرَافِيَّةِ', 'الِاسْتِمَاعُ إِلَى الْأَدَاءِ وَتَقْيِيمُهُ', 'Penguasaan bahasa: menguasai bahasa yang benar dan kaidahnya untuk profesionalisme.')
q(3, 'مَا الِاسْتِمَاعُ وَالتَّقْيِيمُ؟', 'الِاسْتِمَاعُ إِلَى أَدَائِكَ وَتَحْدِيدُ نِقَاطِ الْقُوَّةِ وَالضَّعْفِ', 'تَحْدِيدُ مَخَارِجِ الْحُرُوفِ', 'Mendengarkan penampilan sendiri dan mengenali kekuatan serta kelemahannya.')
q(3, 'مَا النَّبْرُ؟', 'نُطْقُ مَقْطَعٍ مِنْ مَقَاطِعِ الْكَلِمَةِ بِصُورَةٍ أَوْضَحَ مِنْ غَيْرِهِ', 'اخْتِلَافُ دَرَجَةِ الصَّوْتِ بَيْنَ الْجُمَلِ', 'Nabr (tekanan): satu suku kata dilafalkan lebih jelas dari suku kata di sekitarnya.')
q(3, 'فِي كَلِمَةِ «نَاصِرٍ» عَلَى وَزْنِ «فَاعِلٍ» أَيْنَ يَقَعُ النَّبْرُ؟', 'عَلَى حَرْفِ النُّونِ', 'عَلَى حَرْفِ الصَّادِ', 'Pada "naashir", tekanan jatuh pada huruf nun.')
q(3, 'فِي كَلِمَةِ «مَنْصُورٍ» عَلَى وَزْنِ «مَفْعُولٍ» أَيْنَ يَقَعُ النَّبْرُ؟', 'عَلَى حَرْفِ الصَّادِ', 'عَلَى حَرْفِ النُّونِ', 'Pada "manshuur", tekanan jatuh pada huruf shad.')
q(3, 'فِي كَلِمَةِ «مُسْتَنْصِرٍ» عَلَى وَزْنِ «مُسْتَفْعِلٍ» أَيْنَ يَقَعُ النَّبْرُ؟', 'عَلَى حَرْفِ التَّاءِ', 'عَلَى حَرْفِ الْمِيمِ', 'Pada "mustanshir", tekanan jatuh pada huruf ta.')
q(3, 'مَا التَّعْزِيزُ؟', 'إِبْرَازُ كَلِمَاتٍ أَوْ جُمَلٍ بِعَيْنِهَا وَتَوْكِيدُهَا', 'خَفْضُ الصَّوْتِ فِي آخِرِ الْجُمْلَةِ', 'Penguatan (emphasis): menonjolkan kata/kalimat tertentu agar lebih jelas.')
q(3, 'تَعْزِيزُ الْكَلِمَةِ يَعْنِي:', 'رَفْعَ دَرَجَتِهَا لَا رَفْعَ مُسْتَوَى صَوْتِهَا', 'رَفْعَ مُسْتَوَى صَوْتِهَا لَا دَرَجَتِهَا', 'Menguatkan kata berarti menaikkan nadanya (pitch), bukan volumenya.')
q(3, 'مَا التَّنْغِيمُ؟', 'الِاخْتِلَافُ فِي رَفْعِ دَرَجَةِ الصَّوْتِ وَانْخِفَاضِهَا لِلتَّفْرِيقِ بَيْنَ الدَّلَالَاتِ', 'نُطْقُ الْمَقْطَعِ بِوُضُوحٍ أَكْبَرَ', 'Intonasi: naik-turun nada untuk membedakan penegasan, pertanyaan, seruan, dan perasaan.')
q(3, 'مَا الدَّرَجَةُ أَوِ الطَّبَقَةُ؟', 'النَّغْمَةُ الْمُوسِيقِيَّةُ لِصَوْتِ نُطْقِ الْإِنْسَانِ', 'سُرْعَةُ الْمُؤَدِّي فِي لَحْظَةٍ مُعَيَّنَةٍ', 'Pitch/register: nada musikal suara ucapan manusia.')
q(3, 'مَا التَّزْمِينُ؟', 'التَّبَايُنُ فِي سُرْعَةِ الْمُؤَدِّي فِي لَحْظَةٍ مُعَيَّنَةٍ', 'التَّبَايُنُ فِي نَوْعِ الصَّوْتِ', 'Timing: variasi kecepatan pengisi suara pada momen tertentu.')
q(3, 'مَا السَّكْتَةُ؟', 'أَخَفُّ مِنَ الْوَقْفَةِ، وَيُمْكِنُ إِعْمَالُهَا أَوْ إِهْمَالُهَا', 'أَطْوَلُ مِنَ الْوَقْفَةِ وَلَا بُدَّ مِنْهَا', 'Saktah lebih ringan daripada waqfah; boleh diterapkan atau diabaikan, menerapkannya lebih utama.')
q(3, 'مَا الْقَوَاعِدُ الضَّابِطَةُ لِلِاسْتِرَاحَةِ أَوْ أَخْذِ النَّفَسِ؟', 'لَا قَوَاعِدَ ضَابِطَةً لَهَا، وَتَعْتَمِدُ عَلَى قُدْرَةِ الْمُتَكَلِّمِ', 'لَهَا قَوَاعِدُ ثَابِتَةٌ لَا تَتَغَيَّرُ', 'Tidak ada kaidah baku; bergantung pemahaman pembicara atas teks dan kaidah bahasa.')

# ---------------- Bab 10: suku kata
q(4, 'مَا الْمَقْطَعُ فِي الِاصْطِلَاحِ؟', 'أَصْغَرُ وَحْدَةٍ فِي تَرْكِيبِ الْكَلِمَةِ', 'أَكْبَرُ وَحْدَةٍ فِي تَرْكِيبِ الْجُمْلَةِ', 'Suku kata (maqtha\') secara istilah adalah satuan terkecil dalam struktur kata.')
q(4, 'مَا الْمَقْطَعُ فِي اللُّغَةِ؟', 'الْقَطْعُ، وَهُوَ إِبَانَةُ بَعْضِ أَجْزَاءِ الشَّيْءِ', 'الْجَمْعُ وَالضَّمُّ', 'Secara bahasa maqtha\' bermakna pemotongan, yaitu memisahkan sebagian bagian dari sesuatu.')
q(4, 'الْمَقْطَعُ وَحْدَةٌ أَكْبَرُ مِنْ:', 'الْحَرْفِ وَالْحَرَكَةِ', 'الْكَلِمَةِ وَالْجُمْلَةِ', 'Suku kata lebih besar dari huruf dan harakat karena ia gabungan huruf dengan satu harakat atau lebih.')
q(4, 'يُقَسَّمُ الْكَلَامُ إِلَى مَقَاطِعَ بِسَبَبِ تَتَابُعِ:', 'الْحَرْفِ الصَّامِتِ وَالْحَرَكَةِ الصَّائِتَةِ', 'الْفِعْلِ وَالْفَاعِلِ', 'Pembagian suku kata didasarkan pergantian konsonan (K) dan vokal (V).')
q(4, 'الْحَرْفُ مَعَ الْحَرَكَةِ الَّتِي تَحَرَّكَ بِهَا يُصْبِحُ:', 'مَقْطَعًا صَوْتِيًّا', 'كَلِمَةً مُسْتَقِلَّةً', 'Huruf beserta harakatnya telah menjadi satu suku kata.')
q(4, 'التَّنْوِينُ فِي أَصْلِهِ يَعُودُ إِلَى:', 'نُونٍ سَاكِنَةٍ تُضَافُ إِلَى حَرَكَةِ الْحَرْفِ', 'هَمْزَةِ وَصْلٍ', 'Tanwin kembali kepada nun sukun yang ditambahkan pada harakat huruf.')
q(4, 'فِي التَّقْطِيعِ، الْحَرْفُ الْمُتَحَرِّكُ مَعَ نُونِ التَّنْوِينِ السَّاكِنَةِ:', 'مَقْطَعٌ صَوْتِيٌّ وَاحِدٌ', 'مَقْطَعَانِ', 'Huruf berharakat beserta nun sukun tanwin menjadi satu suku kata.')
q(4, 'كَيْفَ تُقَطَّعُ كَلِمَةُ «حَقِيبَةً»؟', 'حَ / قِي / بَ / تَنْ', 'حَقِ / يبَ / تً', 'Ha / qii / ba / tan; tanwin menjadi nun sukun yang menyatu dengan ta.')
q(4, 'حَرْفُ الْمَدِّ مَعَ الْحَرْفِ الَّذِي قَبْلَهُ:', 'مَقْطَعٌ صَوْتِيٌّ وَاحِدٌ', 'مَقْطَعَانِ مُنْفَصِلَانِ', 'Huruf mad beserta huruf sebelumnya satu suku kata.')
q(4, 'كَيْفَ تُقَطَّعُ كَلِمَةُ «مَلْجَآنِ»؟', 'مَلْ / جَ / آ / نِ', 'مَ / لْجَ / آنِ', 'Mal / ja / aa / ni.')
q(4, 'الْحَرْفُ الْمُشَدَّدُ يُعَدُّ بِمَثَابَةِ:', 'تَكْرَارٍ لِلْحَرْفِ نَفْسِهِ', 'حَذْفٍ لِلْحَرْفِ', 'Tasydid dianggap pengulangan huruf; saat diurai, huruf pertama sukun menyatu dengan huruf sebelumnya.')
q(4, 'الْحَرْفُ السَّاكِنُ وَحْدَهُ:', 'لَا يَسْتَطِيعُ تَشْكِيلَ الْمَقْطَعِ الصَّوْتِيِّ', 'يُشَكِّلُ مَقْطَعًا كَامِلًا', 'Huruf sukun harus bergabung dengan huruf sebelumnya untuk membentuk suku kata.')
q(4, 'اللَّامُ الْقَمَرِيَّةُ مَعَ هَمْزَةِ الْوَصْلِ الَّتِي قَبْلَهَا:', 'مَقْطَعٌ صَوْتِيٌّ وَاحِدٌ', 'مَقْطَعَانِ', 'Lam qamariyyah sukun bergabung dengan hamzah washal yang berharakat, seperti pada «al-jabalu».')
q(4, 'كَيْفَ تُقَطَّعُ كَلِمَةُ «الْوَطَنُ»؟', 'الـ / وَ / طَ / نُ', 'الْوَ / طَنُ', 'Al / wa / tha / nu.')
q(4, 'لِمَاذَا لَا تُنْطَقُ اللَّامُ الشَّمْسِيَّةُ؟', 'لِأَنَّ الْحَرْفَ بَعْدَهَا مُشَدَّدٌ', 'لِأَنَّهَا حَرْفٌ زَائِدٌ دَائِمًا', 'Lam syamsiyyah tidak dilafalkan karena huruf setelahnya bertasydid.')
q(4, 'كَيْفَ تُقَطَّعُ كَلِمَةُ «الصَّبَاحُ»؟', 'أَصْ / صَ / بَا / حُ', 'الـ / صَّ / بَا / حُ', 'Ash / sha / baa / hu: syin/shad bertasydid terurai menjadi sukun dan berharakat.')
q(4, 'مَاذَا يُرْمَزُ بِـ (ص) وَ(ح) فِي التَّعْبِيرِ الْمَقْطَعِيِّ؟', 'ص: صَامِتٌ، ح: حَرَكَةٌ صَائِتَةٌ', 'ص: صَائِتٌ، ح: صَامِتٌ', 'Dalam notasi suku kata, ص = konsonan (K) dan ح = vokal (V).')
q(4, 'الْمَقْطَعُ الْقَصِيرُ يَتَكَوَّنُ مِنْ:', 'صَامِتٍ وَحَرَكَةٍ (ص ح)', 'صَامِتٍ وَحَرَكَةٍ وَصَامِتٍ (ص ح ص)', 'Suku kata pendek: K-V, misalnya «a».')
q(4, 'الْمَقْطَعُ الْمُتَوَسِّطُ الْمُغْلَقُ تَعْبِيرُهُ الْمَقْطَعِيُّ:', 'ص ح ص، مِثْلَ «قَدْ»', 'ص ح ح، مِثْلَ «مَا»', 'Sedang tertutup: berakhiran konsonan, K-V-K, contoh «qad».')
q(4, 'الْمَقْطَعُ الْمُتَوَسِّطُ الْمَفْتُوحُ تَعْبِيرُهُ الْمَقْطَعِيُّ:', 'ص ح ح، مِثْلَ «مَا»', 'ص ح ص، مِثْلَ «قَدْ»', 'Sedang terbuka: berakhiran vokal panjang, K-V-V, contoh «maa».')
q(4, 'مَا تَعْبِيرُ مَقْطَعِ «مِين» فِي «الْعَالَمِينَ»؟', 'ص ح ح ص', 'ص ح ص ص', 'Suku kata berakhiran V-K: K-V-V-K.')
q(4, 'مَا تَعْبِيرُ مَقْطَعِ «خَوْفٌ»؟', 'ص ح ص ص', 'ص ح ح ص', 'Suku kata berakhiran K-K: K-V-K-K.')
q(4, 'الْمَقْطَعُ الطَّوِيلُ فِي اللُّغَةِ الْعَرَبِيَّةِ:', 'قَلِيلٌ، وَتَهْرُبُ مِنْهُ اللُّغَةُ بِأَسَالِيبَ مُتَنَوِّعَةٍ', 'كَثِيرٌ جِدًّا وَهُوَ الْأَصْلُ', 'Suku kata panjang jarang dalam bahasa Arab; bahasa ini menghindarinya dengan berbagai gaya.')


def main():
    rnd = random.Random(20260502)
    items = []
    for b, t, ok, no, e in sorted(Q, key=lambda x: BMAP[x[0]]):
        o = [ok, no]
        a = 0
        if rnd.random() < 0.5:
            o.reverse(); a = 1
        items.append({'b': BMAP[b], 'q': t, 'o': o, 'a': a, 'e': e})
    n = len(items)
    s = open(TPL, encoding='utf8').read()
    s = s.replace('<title>Ujian Sejarah Sastra Arab 5 — Bab 1–4</title>', '<title>Latihan Ilmu Lughah 3 — Bab 8–11</title>')
    s = s.replace('<div class="logo ar">ت</div>', '<div class="logo ar">ع</div>')
    s = s.replace('اخْتِبَارُ تَارِيخِ الْأَدَبِ الْعَرَبِيِّ (٥)', 'اخْتِبَارُ عِلْمِ اللُّغَةِ (٣)')
    s = s.replace('Ujian pilihan ganda &middot; Bab 1 sampai Bab 4 &middot; Tingkat 5', 'Latihan pilihan ganda &middot; Bab 8 sampai Bab 11 &middot; Tingkat 5')
    s = s.replace('<b id="nSoal">92</b>', '<b id="nSoal">%d</b>' % n).replace('<span id="tot">92</span>', '<span id="tot">%d</span>' % n)
    s = s.replace('اخْتِبَارِ تَارِيخِ الْأَدَبِ الْعَرَبِيِّ', 'اخْتِبَارِ عِلْمِ اللُّغَةِ')
    s = s.replace("'tarikhadab5.pengaturan'", "'ilmulughah3.pengaturan'")
    s = re.sub(r'const DATA = .*?;\n', lambda m: 'const DATA = ' + json.dumps({'items': items, 'bab': BAB}, ensure_ascii=False) + ';\n', s, count=1, flags=re.S)
    assert 'Tarikh' not in s.split('<script>')[1][:2000]
    if '--check' in sys.argv:
        print(n, 'soal'); return
    open(OUT, 'w', encoding='utf8').write(s)
    from collections import Counter
    print(n, 'soal', Counter(i['b'] for i in items), 'posisi benar', Counter(i['a'] for i in items))

main()
