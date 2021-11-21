# not zero indexed
RARITY ={
    '1' : 'common',
    '2' : 'rare',
    '3' : 'legendary',
    '4' : 'epic',
    '5' : 'mythic'
}




CHESTS_EMOJIS = {
    'common' : '<:common_chest:901798708864253992>',
    'rare' : '<:rare_chest:901798877726924810>',
    'legendary' : '<:legendary_chest:901799227758350426>',
    'epic' : '<:epic_chest:901799469006336080>',
    'mythic' : '<:mythic_chest:901800353757036594>'
}

CHESTS = {
    'common_chest' : {
        'name' : 'common_chest',
        'emoji' : '<:common_chest:901798708864253992>',
        'description' : '',
        'buy_price' : 150,
        'sell_price' : 100
    },
    'rare_chest' : {
        'name' : 'rare_chest',
        'emoji' : '<:rare_chest:901798877726924810>',
        'description' : '',
        'buy_price' : 300,
        'sell_price' : 150
    },
    'legendary_chest' : {
        'name' : 'legendary_chest',
        'emoji' : '<:legendary_chest:901799227758350426>',
        'description' : '',
        'buy_price' : 1000,
        'sell_price' : 800
    },
    'epic_chest' : {
        'name' : 'epic_chest',
        'emoji' : '<:epic_chest:901799469006336080>',
        'description' : '',
        'buy_price' : None,
        'sell_price' : 1500
    },
    'mythic_chest' : {
        'name' : 'mythic_chest',
        'emoji' : '<:mythic_chest:901800353757036594>',
        'description' : '',
        'buy_price' : None,
        'sell_price' : 3000
    },
}

EMOJIS = {
    'exp' : '<:exp:896086434946097162>',
    'greentick' : '<:greentick:880695423516430336>',
    'redtick' : '<:redTick:876471581054996550>',
    'toggle_on' : '<:toggle_on:890713040880795699>',
    'toggle_off' : '<:toggle_off:890712914330271764>',
    'sd_loading' : '<a:sd_loading:911667761577611315>'
    
}

CD_UNIT = int(18)
# games items

WEAPONS = {
    'p92' : {
        'name' : 'p92_pistol',
        'rarity' : 'common',
        'emoji' : '<:p92:901725176130052126>',
        'ammo' : '9mm',
        'damage' : '15-18',
        'damage_type' : 'single_target',
        'cooldown' : CD_UNIT*18,
        'buy_price' : 150,
        'sell_price' : 100
    },
    'p18c' : {
        'name' : 'p18c_pistol',
        'rarity' : 'rare',
        'emoji' : '<:p18c:901725472780591144>',
        'ammo' : '9mm',
        'damage' : '20-25',
        'damage_type' : 'single_target',
        'cooldown' : CD_UNIT*25,
        'buy_price' : 200,
        'sell_price' : 150
    },
    'grenade' : {
        'name' : 'grenade',
        'rarity' : 'legendary',
        'emoji' : '<:grenade:901571735403528294>',
        'ammo' : None,
        'damage' : '30-40',
        'damage_type' : 'burst_damage',
        'cooldown' : CD_UNIT*40,
        'buy_price' : None,
        'sell_price' : 800
    },
    'ak_47' : {
        'name' : 'ak_47',
        'rarity' : 'legendary',
        'emoji' : '<:ak_47:901570473786228796>',
        'ammo' : '7_62mm',
        'damage' : '35-50',
        'damage_type' : 'single_target',
        'cooldown' : CD_UNIT*50,
        'buy_price' : None,
        'sell_price' : 1200
    },
    'm416' : {
        'name' : 'm416',
        'rarity' : 'legendary',
        'emoji' : '<:m416:901570478538391603>',
        'ammo' : '5_56mm',
        'damage' : '38-45',
        'damage_type' : 'single_target',
        'cooldown' : CD_UNIT*45,
        'buy_price' : None,
        'sell_price' : 1000
    },
    'scar_l' : {
        'name' : 'scar_l',
        'rarity' : 'legendary',
        'emoji' : '<:scar_l:901570493432336385>',
        'ammo' : '5_56mm',
        'damage' : '35-40',
        'damage_type' : 'single_target',
        'cooldown' : CD_UNIT*40,
        'buy_price' : None,
        'sell_price' : 900
    },
    'ump45' : {
        'name' : 'ump45',
        'rarity' : 'rare',
        'emoji' : '<:ump45:901570488692793394>',
        'ammo' : '45acp',
        'damage' : '28-33',
        'damage_type' : 'single_target',
        'cooldown' : CD_UNIT*33,
        'buy_price' : None,
        'sell_price' : 800
    },
    'thompson' : {
        'name' : 'thompson',
        'rarity' : 'rare',
        'emoji' : '<:thompson:901767201537818664>',
        'ammo' : '45acp',
        'damage' : '25-30',
        'damage_type' : 'single_target',
        'cooldown' : CD_UNIT*30,
        'buy_price' : None,
        'sell_price' : 700
    },
    'vector' : {
        'name' : 'thompson',
        'rarity' : 'legendary',
        'emoji' : '<:vector:901571514762137692>',
        'ammo' : '45acp',
        'damage' : '33-40',
        'damage_type' : 'single_target',
        'cooldown' : CD_UNIT*40,
        'buy_price' : None,
        'sell_price' : 850
    },
    'win94' : {
        'name' : 'win94',
        'rarity' : 'epic',
        'emoji' : '<:win94:901571519682072598>',
        'ammo' : '45acp',
        'damage' : '60-75',
        'damage_type' : 'single_target',
        'cooldown' : CD_UNIT*75,
        'buy_price' : None,
        'sell_price' : 2000
    },
    'kar98k' : {
        'name' : 'kar98k',
        'rarity' : 'epic',
        'emoji' : '<:kar98k_sniper_rifle:901570666774548570>',
        'ammo' : '7_62mm',
        'damage' : '70-80',
        'damage_type' : 'single_target',
        'cooldown' : CD_UNIT*80,
        'buy_price' : None,
        'sell_price' : 2200
    },
    'm24' : {
        'name' : 'm24',
        'rarity' : 'epic',
        'emoji' : '<:m24_sniper_rifle:901571401503342674>',
        'ammo' : '7_62mm',
        'damage' : '75-85',
        'damage_type' : 'single_target',
        'cooldown' : CD_UNIT*85,
        'buy_price' : None,
        'sell_price' : 2300
    },
    'awm' : {
        'name' : 'awm',
        'rarity' : 'mythic',
        'emoji' : '<:awm_sniper_rifle:901570671769964544>',
        'ammo' : '300magnum',
        'damage' : '85-100',
        'damage_type' : 'single_target',
        'cooldown' : CD_UNIT*100,
        'buy_price' : None,
        'sell_price' : 3500
    },
    'groza' : {
        'name' : 'groza',
        'rarity' : 'epic',
        'emoji' : '<:groza:901571406523953162>',
        'ammo' : '7_62mm',
        'damage' : '48-63',
        'damage_type' : 'single_target',
        'cooldown' : CD_UNIT*63,
        'buy_price' : None,
        'sell_price' : 2000
    },
    'beryl' : {
        'name' : 'beryl',
        'rarity' : 'legendary',
        'emoji' : '<:beryl_m762:901571411414487041>',
        'ammo' : '7_62mm',
        'damage' : '38-48',
        'damage_type' : 'single_target',
        'cooldown' : CD_UNIT*48,
        'buy_price' : None,
        'sell_price' : 1150
    },
    'mini14' : {
        'name' : 'mini14',
        'rarity' : 'epic',
        'emoji' : '<:mini14:901787010329612358>',
        'ammo' : '5_56mm',
        'damage' : '48-55',
        'damage_type' : 'single_target',
        'cooldown' : CD_UNIT*55,
        'buy_price' : None,
        'sell_price' : 1600
    },
    'pan' : {
        'name' : 'pan',
        'rarity' : 'rare',
        'emoji' : '<:pan:901575943699697685>',
        'ammo' : None,
        'damage' : '22-27',
        'damage_type' : 'single_target',
        'cooldown' : CD_UNIT*27,
        'buy_price' : None,
        'sell_price' : 250
    },
    'crowbar' : {
        'name' : 'crowbar',
        'rarity' : 'common',
        'emoji' : '<:crowbar:901571396101111830>',
        'ammo' : None,
        'damage' : '12-15',
        'damage_type' : 'single_target',
        'cooldown' : CD_UNIT*15,
        'buy_price' : 100,
        'sell_price' : 80
    },
    'sickle' : {
        'name' : 'sickle',
        'rarity' : 'common',
        'emoji' : '<:sickle:901576064659239013>',
        'ammo' : None,
        'damage' : '12-14',
        'damage_type' : 'single_target',
        'cooldown' : CD_UNIT*14,
        'buy_price' : 90,
        'sell_price' : 75
    },
    's686' : {
        'name' : 's686',
        'rarity' : 'legendary',
        'emoji' : '<:s686:901787362458218506>',
        'ammo' : '12gauge',
        'damage' : '28-38',
        'damage_type' : 'burst_damage',
        'cooldown' : CD_UNIT*38,
        'buy_price' : None,
        'sell_price' : 750
    },
    's1897' : {
        'name' : 's1897',
        'rarity' : 'rare',
        'emoji' : '<:s1897:901787644135092224>',
        'ammo' : '12gauge',
        'damage' : '18-25',
        'damage_type' : 'burst_damage',
        'cooldown' : CD_UNIT*25,
        'buy_price' : None,
        'sell_price' : 500
    },
}

HEALING_ITEMS = {
    'pain_killer' : {
        'name' : 'pain_killer',
        'rarity' : 'rare',
        'emoji' : '<:painkiller:901570677105123378>',
        'hp_recover' : '15-20',
        'cooldown' : CD_UNIT*15,
        'buy_price' : 75,
        'sell_price' : 60
    },
    'bandage' : {
        'name' : 'bandage',
        'rarity' : 'common',
        'emoji' : '<:bandage:901574043449319434>',
        'hp_recover' : '7-12',
        'cooldown' : CD_UNIT*7,
        'buy_price' : 50,
        'sell_price' : 35
    },
    'first_aid_kit' : {
        'name' : 'first_aid_kit',
        'rarity' : 'legendary',
        'emoji' : '<:first_aid_kit:901570962863046706>',
        'hp_recover' : '50-75',
        'cooldown' : CD_UNIT*50,
        'buy_price' : 300,
        'sell_price' : 250
    },
    'med_kit' : {
        'name' : 'med_kit',
        'rarity' : 'epic',
        'emoji' : '<:medkit:901570967707467877>',
        'hp_recover' : '75-100',
        'cooldown' : CD_UNIT*75,
        'buy_price' : None,
        'sell_price' : 500
    },
}

ARMOURS = {
    'police_vest_level_1' : {
        'name' : 'police_vest_level_1',
        'rarity' : 'common',
        'emoji' : '<:police_vest_lvl_1:901511044973867098>',
        'shield_points' : 20,
        'buy_price' : 500,
        'sell_price' : 400
    },
    'police_vest_level_2' : {
        'name' : 'police_vest_level_2',
        'rarity' : 'rare',
        'emoji' : '<:police_vest_lvl_2:901511128188854272>',
        'shield_points' : 30,
        'buy_price' : 600,
        'sell_price' : 450
    },
    'military_armour_level_1' : {
        'name' : 'military_armour_level_1',
        'rarity' : 'legendary',
        'emoji' : '<:military_armour_lvl_1:901511267653652610>',
        'shield_points' : 50,
        'buy_price' : 1000,
        'sell_price' : 800
    },
    'military_armour_level_2' : {
        'name' : 'military_armour_level_2',
        'rarity' : 'epic',
        'emoji' : '<:military_armour_lvl_2:902144891692400660>',
        'shield_points' : 75,
        'buy_price' : None,
        'sell_price' : 2000
    },
    'samurai_armour_set' : {
        'name' : 'samurai_armour_set',
        'rarity' : 'mythic',
        'emoji' : '<:samurai_armour_set:901510924207276122>',
        'shield_points' : 100,
        'buy_price' : None,
        'sell_price' : 3000
    },
}

AMMO ={
    '9mm' : {
        'name' : '9mm_bullet',
        'emoji' : '<:9mm:901772563825438720>',
        'rarity' : 'common',
        'used_by' : ['p92', 'p18c', 'uzi'],
        'sell_price' : 75
    },
    '45acp' : {
        'name' : '45acp_bullet',
        'emoji' : '<:45acp:901772580552323102>',
        'rarity' : 'rare',
        'used_by' : ['thompson','ump45', 'win94', 'desert_eagle', 'vector'],
        'sell_price' : 150
    },
    '5_56mm' : {
        'name' : '5_56mm_bullet',
        'emoji' : '<:5_56mm:901772574843867217>',
        'rarity' : 'legendary',
        'used_by' : ['m416', 'scar_l', 'mini14'],
        'sell_price' : 220
    },
    '7_62mm' : {
        'name' : '7_62mm_bullet',
        'emoji' : '<:7_62mm:901772569349357598>',
        'rarity' : 'legendary',
        'used_by' : ['ak_47', 'groza', 'beryl', 'kar98k', 'm24'],
        'sell_price' : 250
    },
    '300magnum' : {
        'name' : '300magnum_bullet',
        'emoji' : '<:300magnum:901772585665187840>',
        'rarity' : 'epic',
        'used_by' : ['awm'],
        'sell_price' : 450
    },
    '12gauge' : {
        'name' : '12gauge_shells',
        'emoji' : '<:12gauge:901772615570579537>',
        'rarity' : 'rare',
        'used_by' : ['s686', 's1897'],
        'sell_price' : 100
    },
}



COOLDOWNS = {
    'hourly' : 3600,
    'daily' : 86400,
    'weekly' : 604800,
    'monthly' : 2592000,
    'work' : 5400,
    'loot' : 30,
    'opt_in_toggle' : 43200,
    'w_equip' : 300,
    'a_equip' : 300
}

EXP_LEVELS = {
    '1' : 500,
    '2' : 1100,
    '3' : 1800,
    '4' : 2000,
    '5' : 3500,
    '6' : 5500,
    '7' : 8000,
    '8' : 11000,
    '9' : 14500,
    '10' : 18500,
    '11' : 23000,
    '12' : 28000,
    '14' : 33500,
    '15' : 39500,
    '16' : 46000,
    '17' : 52500,
    '18' : 59000,
    '19' : 66000
}

HP_EMOJIS = {
    'left_full' : '<:hp_l_full:902306058398203905>',
    'left_half' : '<:hp_l_half:902309398909689856>',
    'middle_full' : '<:hp_m_full:902306480156442674>',
    'middle_half' : '<:hp_m_half:902311217115316344>',
    'right_full' : '<:hp_r_full:902306574637338664>',
    'right_half' : '<:hp_r_half:902308931232231425>',
    'middle_empty' : '<:m_empty:902308055167930438>',
    'right_empty' : '<:r_empty:902307804860284968>'
}

SHIELD_EMOJIS = {
    'left_full' : '<:sh_l_full:902456199667134464>',
    'left_half' : '<:sh_l_half:902456898106826763>',
    'middle_full' : '<:sh_m_full:902456332899209217>',
    'middle_half' : '<:sh_m_half:902456433931599902>',
    'right_full' : '<:sh_r_full:902458981358919711>',
    'right_half' : '<:sh_r_half:902458685786296340>',
    'middle_empty' : '<:m_empty:902308055167930438>',
    'right_empty' : '<:r_empty:902307804860284968>'
}
EXP_EMOJIS = {
    'left_full' : '<:exp_l_full:902306957342421052>',
    'left_half' : '<:exp_l_half:902459783909613599>',
    'middle_full' : '<:exp_m_full:902307086363398254>',
    'middle_half' : '<:exp_m_half:902460294104764416>',
    'right_full' : '<:exp_r_full:902460647927853067>',
    'right_half' : '<:exp_r_half:902461637099933736>',
    'middle_empty' : '<:m_empty:902308055167930438>',
    'right_empty' : '<:r_empty:902307804860284968>'
}

RARITY_INDEX ={
    'common' : 0,
    'rare' : 1,
    'legendary' : 2,
    'epic' : 3,
    'mythic' : 4
}
