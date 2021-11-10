


CD_UNIT = int(36)
ALL_ITEMS = {
    'p92' : {
        'name' : 'p92',
        'type' : 'weapon',
        'rarity' : 'common',
        'emoji' : '<:p92:901725176130052126>',
        'ammo' : '9mm',
        'damage' : '15-18',
        'damage_type' : 'single target',
        'cooldown' : CD_UNIT*18,
        'buy_price' : 150,
        'sell_price' : 100
    },
    'p18c' : {
        'name' : 'p18c',
        'type' : 'weapon',
        'rarity' : 'rare',
        'emoji' : '<:p18c:901725472780591144>',
        'ammo' : '9mm',
        'damage' : '20-25',
        'damage_type' : 'single target',
        'cooldown' : CD_UNIT*25,
        'buy_price' : 200,
        'sell_price' : 150
    },
    'grenade' : {
        'name' : 'grenade',
        'type' : 'weapon',
        'rarity' : 'legendary',
        'emoji' : '<:grenade:901571735403528294>',
        'ammo' : None,
        'damage' : '30-40',
        'damage_type' : 'burst damage',
        'cooldown' : CD_UNIT*40,
        'buy_price' : None,
        'sell_price' : 800
    },
    'ak_47' : {
        'name' : 'ak 47',
        'type' : 'weapon',
        'rarity' : 'legendary',
        'emoji' : '<:ak_47:901570473786228796>',
        'ammo' : '7_62mm',
        'damage' : '35-50',
        'damage_type' : 'single target',
        'cooldown' : CD_UNIT*50,
        'buy_price' : None,
        'sell_price' : 1200
    },
    'm416' : {
        'name' : 'm416',
        'type' : 'weapon',
        'rarity' : 'legendary',
        'emoji' : '<:m416:901570478538391603>',
        'ammo' : '5_56mm',
        'damage' : '38-45',
        'damage_type' : 'single target',
        'cooldown' : CD_UNIT*45,
        'buy_price' : None,
        'sell_price' : 1000
    },
    'scar_l' : {
        'name' : 'scar l',
        'type' : 'weapon',
        'rarity' : 'legendary',
        'emoji' : '<:scar_l:901570493432336385>',
        'ammo' : '5_56mm',
        'damage' : '35-40',
        'damage_type' : 'single target',
        'cooldown' : CD_UNIT*40,
        'buy_price' : None,
        'sell_price' : 900
    },
    'ump45' : {
        'name' : 'ump45',
        'type' : 'weapon',
        'rarity' : 'rare',
        'emoji' : '<:ump45:901570488692793394>',
        'ammo' : '45acp',
        'damage' : '28-33',
        'damage_type' : 'single target',
        'cooldown' : CD_UNIT*33,
        'buy_price' : None,
        'sell_price' : 800
    },
    'thompson' : {
        'name' : 'thompson',
        'type' : 'weapon',
        'rarity' : 'rare',
        'emoji' : '<:thompson:901767201537818664>',
        'ammo' : '45acp',
        'damage' : '25-30',
        'damage_type' : 'single target',
        'cooldown' : CD_UNIT*30,
        'buy_price' : None,
        'sell_price' : 700
    },
    'vector' : {
        'name' : 'vector',
        'type' : 'weapon',
        'rarity' : 'legendary',
        'emoji' : '<:vector:901571514762137692>',
        'ammo' : '45acp',
        'damage' : '33-40',
        'damage_type' : 'single target',
        'cooldown' : CD_UNIT*40,
        'buy_price' : None,
        'sell_price' : 850
    },
    'win94' : {
        'name' : 'win94',
        'type' : 'weapon',
        'rarity' : 'epic',
        'emoji' : '<:win94:901571519682072598>',
        'ammo' : '45acp',
        'damage' : '60-75',
        'damage_type' : 'single target',
        'cooldown' : CD_UNIT*75,
        'buy_price' : None,
        'sell_price' : 2000
    },
    'kar98k' : {
        'name' : 'kar98k',
        'type' : 'weapon',
        'rarity' : 'epic',
        'emoji' : '<:kar98k_sniper_rifle:901570666774548570>',
        'ammo' : '7_62mm',
        'damage' : '70-80',
        'damage_type' : 'single target',
        'cooldown' : CD_UNIT*80,
        'buy_price' : None,
        'sell_price' : 2200
    },
    'm24' : {
        'name' : 'm24',
        'type' : 'weapon',
        'rarity' : 'epic',
        'emoji' : '<:m24_sniper_rifle:901571401503342674>',
        'ammo' : '7_62mm',
        'damage' : '75-85',
        'damage_type' : 'single target',
        'cooldown' : CD_UNIT*85,
        'buy_price' : None,
        'sell_price' : 2300
    },
    'awm' : {
        'name' : 'awm',
        'type' : 'weapon',
        'rarity' : 'mythic',
        'emoji' : '<:awm_sniper_rifle:901570671769964544>',
        'ammo' : '300magnum',
        'damage' : '85-100',
        'damage_type' : 'single target',
        'cooldown' : CD_UNIT*100,
        'buy_price' : None,
        'sell_price' : 3500
    },
    'groza' : {
        'name' : 'groza',
        'type' : 'weapon',
        'rarity' : 'epic',
        'emoji' : '<:groza:901571406523953162>',
        'ammo' : '7_62mm',
        'damage' : '48-63',
        'damage_type' : 'single target',
        'cooldown' : CD_UNIT*63,
        'buy_price' : None,
        'sell_price' : 2000
    },
    'beryl' : {
        'name' : 'beryl',
        'type' : 'weapon',
        'rarity' : 'legendary',
        'emoji' : '<:beryl_m762:901571411414487041>',
        'ammo' : '7_62mm',
        'damage' : '38-48',
        'damage_type' : 'single target',
        'cooldown' : CD_UNIT*48,
        'buy_price' : None,
        'sell_price' : 1150
    },
    'mini14' : {
        'name' : 'mini14',
        'type' : 'weapon',
        'rarity' : 'epic',
        'emoji' : '<:mini14:901787010329612358>',
        'ammo' : '5_56mm',
        'damage' : '48-55',
        'damage_type' : 'single target',
        'cooldown' : CD_UNIT*55,
        'buy_price' : None,
        'sell_price' : 1600
    },
    'pan' : {
        'name' : 'pan',
        'type' : 'weapon',
        'rarity' : 'rare',
        'emoji' : '<:pan:901575943699697685>',
        'ammo' : None,
        'damage' : '22-27',
        'damage_type' : 'single target',
        'cooldown' : CD_UNIT*27,
        'buy_price' : None,
        'sell_price' : 250
    },
    'crowbar' : {
        'name' : 'crowbar',
        'type' : 'weapon',
        'rarity' : 'common',
        'emoji' : '<:crowbar:901571396101111830>',
        'ammo' : None,
        'damage' : '12-15',
        'damage_type' : 'single target',
        'cooldown' : CD_UNIT*15,
        'buy_price' : 100,
        'sell_price' : 80
    },
    'sickle' : {
        'name' : 'sickle',
        'type' : 'weapon',
        'rarity' : 'common',
        'emoji' : '<:sickle:901576064659239013>',
        'ammo' : None,
        'damage' : '12-14',
        'damage_type' : 'single target',
        'cooldown' : CD_UNIT*14,
        'buy_price' : 90,
        'sell_price' : 75
    },
    's686' : {
        'name' : 's686',
        'type' : 'weapon',
        'rarity' : 'legendary',
        'emoji' : '<:s686:901787362458218506>',
        'ammo' : '12gauge',
        'damage' : '28-38',
        'damage_type' : 'burst damage',
        'cooldown' : CD_UNIT*38,
        'buy_price' : None,
        'sell_price' : 750
    },
    's1897' : {
        'name' : 's1897',
        'type' : 'weapon',
        'rarity' : 'rare',
        'emoji' : '<:s1897:901787644135092224>',
        'ammo' : '12gauge',
        'damage' : '18-25',
        'damage_type' : 'burst damage',
        'cooldown' : CD_UNIT*25,
        'buy_price' : None,
        'sell_price' : 500
    },
    'pain_killer' : {
        'name' : 'pain killer',
        'type' : 'healing',
        'rarity' : 'rare',
        'emoji' : '<:painkiller:901570677105123378>',
        'hp_recover' : '15-20',
        'cooldown' : CD_UNIT*15,
        'buy_price' : 75,
        'sell_price' : 60
    },
    'bandage' : {
        'name' : 'bandage',
        'type' : 'healing',
        'rarity' : 'common',
        'emoji' : '<:bandage:901574043449319434>',
        'hp_recover' : '7-12',
        'cooldown' : CD_UNIT*7,
        'buy_price' : 50,
        'sell_price' : 35
    },
    'first_aid_kit' : {
        'name' : 'first aid kit',
        'type' : 'healing',
        'rarity' : 'legendary',
        'emoji' : '<:first_aid_kit:901570962863046706>',
        'hp_recover' : '50-75',
        'cooldown' : CD_UNIT*50,
        'buy_price' : 300,
        'sell_price' : 250
    },
    'med_kit' : {
        'name' : 'med kit',
        'type' : 'healing',
        'rarity' : 'epic',
        'emoji' : '<:medkit:901570967707467877>',
        'hp_recover' : '75-100',
        'cooldown' : CD_UNIT*75,
        'buy_price' : None,
        'sell_price' : 500
    },
    'police_vest_level_1' : {
        'name' : 'police vest level 1',
        'type' : 'armour',
        'rarity' : 'common',
        'emoji' : '<:police_vest_lvl_1:901511044973867098>',
        'shield_points' : 20,
        'buy_price' : 500,
        'sell_price' : 400
    },
    'police_vest_level_2' : {
        'name' : 'police vest level 2',
        'type' : 'armour',
        'rarity' : 'rare',
        'emoji' : '<:police_vest_lvl_2:901511128188854272>',
        'shield_points' : 30,
        'buy_price' : 600,
        'sell_price' : 450
    },
    'military_armour_level_1' : {
        'name' : 'military armour level 1',
        'type' : 'armour',
        'rarity' : 'legendary',
        'emoji' : '<:military_armour_lvl_1:901511267653652610>',
        'shield_points' : 50,
        'buy_price' : 1000,
        'sell_price' : 800
    },
    'military_armour_level_2' : {
        'name' : 'military armour level 2',
        'type' : 'armour',
        'rarity' : 'epic',
        'emoji' : '<:military_armour_lvl_2:902144891692400660>',
        'shield_points' : 75,
        'buy_price' : None,
        'sell_price' : 2000
    },
    'samurai_armour_set' : {
        'name' : 'samurai armour set',
        'type' : 'armour',
        'rarity' : 'mythic',
        'emoji' : '<:samurai_armour_set:901510924207276122>',
        'shield_points' : 100,
        'buy_price' : None,
        'sell_price' : 3000
    },
    '9mm' : {
        'name' : '9mm bullet',
        'type' : 'ammunition',
        'emoji' : '<:9mm:901772563825438720>',
        'rarity' : 'common',
        'used_by' : ['p92', 'p18c', 'uzi'],
        'buy_price' : None,
        'sell_price' : 75
    },
    '45acp' : {
        'name' : '45acp bullet',
        'type' : 'ammunition',
        'emoji' : '<:45acp:901772580552323102>',
        'rarity' : 'rare',
        'used_by' : ['thompson','ump45', 'win94', 'desert_eagle', 'vector'],
        'buy_price' : None,
        'sell_price' : 150
    },
    '5_56mm' : {
        'name' : '5.56mm bullet',
        'type' : 'ammunition',
        'emoji' : '<:5_56mm:901772574843867217>',
        'rarity' : 'legendary',
        'used_by' : ['m416', 'scar_l', 'mini14'],
        'buy_price' : None,
        'sell_price' : 220
    },
    '7_62mm' : {
        'name' : '7.62mm bullet',
        'type' : 'ammunition',
        'emoji' : '<:7_62mm:901772569349357598>',
        'rarity' : 'legendary',
        'used_by' : ['ak_47', 'groza', 'beryl', 'kar98k', 'm24'],
        'buy_price' : None,
        'sell_price' : 250
    },
    '300magnum' : {
        'name' : '.300magnum bullet',
        'type' : 'ammunition',
        'emoji' : '<:300magnum:901772585665187840>',
        'rarity' : 'epic',
        'used_by' : ['awm'],
        'buy_price' : None,
        'sell_price' : 450
    },
    '12gauge' : {
        'name' : '12gauge shells',
        'type' : 'ammunition',
        'emoji' : '<:12gauge:901772615570579537>',
        'rarity' : 'rare',
        'used_by' : ['s686', 's1897'],
        'buy_price' : None,
        'sell_price' : 100
    },
    'common_chest' : {
        'name' : 'common chest',
        'type' : 'chest',
        'rarity' : 'common',
        'emoji' : '<:common_chest:901798708864253992>',
        'description' : 'soon',
        'buy_price' : 150,
        'sell_price' : 100
    },
    'rare_chest' : {
        'name' : 'rare chest',
        'type' : 'chest',
        'rarity' : 'rare',
        'emoji' : '<:rare_chest:901798877726924810>',
        'description' : 'soon',
        'buy_price' : 300,
        'sell_price' : 150
    },
    'legendary_chest' : {
        'name' : 'legendary chest',
        'type' : 'chest',
        'rarity' : 'legendary',
        'emoji' : '<:legendary_chest:901799227758350426>',
        'description' : 'soon',
        'buy_price' : 1000,
        'sell_price' : 800
    },
    'epic_chest' : {
        'name' : 'epic chest',
        'type' : 'chest',
        'rarity' : 'epic',
        'emoji' : '<:epic_chest:901799469006336080>',
        'description' : 'soon',
        'buy_price' : None,
        'sell_price' : 1500
    },
    'mythic_chest' : {
        'name' : 'mythic chest',
        'type' : 'chest',
        'rarity' : 'mythic',
        'emoji' : '<:mythic_chest:901800353757036594>',
        'description' : 'soon',
        'buy_price' : None,
        'sell_price' : 3000
    },
} 

COMMON_ITEMS_LIST = ['p92', 'crowbar', 'sickle', 'bandage', 'police_vest_level_1', '9mm', 'common_chest']

RARE_ITEMS_LIST = ['p18c', 'ump45', 'thompson', 'pan', 's1897', 'pain_killer', 'police_vest_level_2', '45acp', '12gauge', 'rare_chest']

LEGENDARY_ITEMS_LIST = ['grenade', 'ak_47', 'm416', 'scar_l', 'vector', 'beryl', 's686', 'first_aid_kit', 'military_armour_level_1', '5_56mm', '7_62mm', 'legendary_chest']

EPIC_ITEMS_LIST = ['win94', 'kar98k', 'm24', 'groza', 'mini14', 'med_kit', 'military_armour_level_2', '300magnum', 'epic_chest']

MYTHIC_ITEMS_LIST = ['awm', 'samurai_armour_set', 'mythic_chest']

RARITY_BASED_LIST =  [COMMON_ITEMS_LIST, RARE_ITEMS_LIST, LEGENDARY_ITEMS_LIST, EPIC_ITEMS_LIST, MYTHIC_ITEMS_LIST]
