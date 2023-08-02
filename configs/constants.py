# A 700MiB CD can reach ~80min at the maxmium
MAX_SINGLE_CD_DURATION_MS : int = 80 * 60 * 1000

# these are used to detect ass language
UNIQUE_CHARS = {
    'chs': '这为来个们说国时于会后对着过发军无么经当与学进种将还见没从动现开长样实两问头机并间关应门点东战业内儿书制体话产声马处给数义几则气员论别听万尔报总张师许条变计认结题却难务场电边统亲请风资传领决队强区达权设观记议带据云觉飞远众车类转该连术济干运让识规极争备阳尽华称罗爱导确办节击陈兴虽杀准广黄满单联调须离证约组随视断党县轻质语况举钱历乐写团诸闻余价号级参红图礼营际汉显亚线终选龙势属农谓费谈专吗装绝敌刘宝愿严归医护卫岁标响细职讲独责较苏双围仅纪谁惊维斗构验紧异宫乱银户游采态够划续试伤刚状兰诉征胜项继爷齐脸热怀纳执欢灵药监织陆孙罢劳获旧网预贵错树临诗财适圣弹妇创习负败御讨范冲寻恶险谢环脑静养积镇诏简宁检铁顾读挥杨梦阵买占楼顺阴担妈坚阶吴审剑层脚乡谋协赵减鲁释顿录税优丽遗画鱼坏杂渐压贼温帮换艺赶误钟块饭货补毕隐骑郑叶载荣庄岛脱盖词枪虑献笔仪',
    'cht': '這為來個們說國時於會後對著過發軍無麼經當與學進種將還見沒從動現開長樣實兩問頭機並間關應門點東戰業內兒書製體話產聲馬處給數義幾則氣員論別聽萬爾報總張師許條變計認結題卻難務場電邊統親請風資傳領決隊強區達權設觀記議帶據雲覺飛遠眾車類轉該連術濟幹運讓識規極爭備陽盡華稱羅愛導確辦節擊陳興雖殺準廣黃滿單聯調須離證約組隨視斷黨縣輕質語況舉錢歷樂寫團諸聞餘價號級參紅圖禮營際漢顯亞線終選龍勢屬農謂費談專嗎裝絕敵劉寶願嚴歸醫護衛歲標響細職講獨責較蘇雙圍僅紀誰驚維鬥構驗緊異宮亂銀戶遊採態夠劃續試傷剛狀蘭訴徵勝項繼爺齊臉熱懷納執歡靈藥監織陸孫罷勞獲舊網預貴錯樹臨詩財適聖彈婦創習負敗禦討範衝尋惡險謝環腦靜養積鎮詔簡寧檢鐵顧讀揮楊夢陣買佔樓順陰擔媽堅階吳審劍層腳鄉謀協趙減魯釋頓錄稅優麗遺畫魚壞雜漸壓賊溫幫換藝趕誤鐘塊飯貨補畢隱騎鄭葉載榮莊島脫蓋詞槍慮獻筆儀',
    'jp': '♨⛩✴ぁあぃいぅうぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわゐゑをんゔゕゖ゚゛゜ゝゞゟ゠ァアィイゥウェエォオカガキギクグケゲコゴサザシジスズセゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロヮワヰヱヲンヴヵヶヷヸヹヺ・ーヽヾヿ㊗㊙㍐㍿️',
}