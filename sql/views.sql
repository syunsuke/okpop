-- ============================================================
-- 基本人口
-- ============================================================

DROP VIEW IF EXISTS view_base_data;

CREATE VIEW view_base_data AS

-- 国勢調査
SELECT
    observation_date,
    area_name,
    total_population,
    male_population,
    female_population,
    total_households,
    'census' AS source
FROM census

UNION ALL

-- 修正人口
SELECT
    observation_date,
    area_name,
    total_population,
    male_population,
    female_population,
    total_households,
    'hosei' AS source
FROM hosei

UNION ALL

-- 修正人口が存在しない年月だけ推計人口を使用
SELECT
    s.observation_date,
    s.area_name,
    s.total_population,
    s.male_population,
    s.female_population,
    s.total_households,
    'suikei' AS source
FROM suikei AS s
WHERE NOT EXISTS (
    SELECT 1
    FROM hosei AS h
    WHERE h.observation_date = s.observation_date
      AND h.area_name = s.area_name
);


-- ============================================================
-- 月次人口増減
-- ============================================================

DROP VIEW IF EXISTS view_monthly_change_data;

CREATE VIEW view_monthly_change_data AS

SELECT
    observation_date,
    area_name,
    monthly_population_change,
    monthly_natural_change,
    births_monthly,
    deaths_monthly,
    monthly_net_migration
FROM suikei;


-- ============================================================
-- 5歳階級：通常版
--
-- V002のみを使用
-- 85-89 / 90-94 / 95歳以上を個別に保持
-- ============================================================

DROP VIEW IF EXISTS view_age_5year_groups;

CREATE VIEW view_age_5year_groups AS

SELECT
    observation_date,
    area_name,
    sex,
    age_total,
    age_00_04,
    age_05_09,
    age_10_14,
    age_15_19,
    age_20_24,
    age_25_29,
    age_30_34,
    age_35_39,
    age_40_44,
    age_45_49,
    age_50_54,
    age_55_59,
    age_60_64,
    age_65_69,
    age_70_74,
    age_75_79,
    age_80_84,
    age_85_89,
    age_90_94,
    age_95plus
FROM population_age5_v002;


-- ============================================================
-- 5歳階級：short版
--
-- V001とV002を共通形式にする
-- 85歳以上は age_85plus にまとめる
-- ============================================================

DROP VIEW IF EXISTS view_age_5year_short_groups;

CREATE VIEW view_age_5year_short_groups AS

-- V001
SELECT
    observation_date,
    area_name,
    sex,
    age_total,
    age_00_04,
    age_05_09,
    age_10_14,
    age_15_19,
    age_20_24,
    age_25_29,
    age_30_34,
    age_35_39,
    age_40_44,
    age_45_49,
    age_50_54,
    age_55_59,
    age_60_64,
    age_65_69,
    age_70_74,
    age_75_79,
    age_80_84,
    age_85plus
FROM population_age5_v001

UNION ALL

-- V002
SELECT
    observation_date,
    area_name,
    sex,
    age_total,
    age_00_04,
    age_05_09,
    age_10_14,
    age_15_19,
    age_20_24,
    age_25_29,
    age_30_34,
    age_35_39,
    age_40_44,
    age_45_49,
    age_50_54,
    age_55_59,
    age_60_64,
    age_65_69,
    age_70_74,
    age_75_79,
    age_80_84,
    age_85_89
        + age_90_94
        + age_95plus
        AS age_85plus
FROM population_age5_v002;


-- ============================================================
-- 5歳階級割合：通常版
-- ============================================================

DROP VIEW IF EXISTS view_age_5year_groups_rate;

CREATE VIEW view_age_5year_groups_rate AS

SELECT
    observation_date,
    area_name,
    sex,

    1.0 * age_00_04 / age_total AS age_00_04_rate,
    1.0 * age_05_09 / age_total AS age_05_09_rate,
    1.0 * age_10_14 / age_total AS age_10_14_rate,
    1.0 * age_15_19 / age_total AS age_15_19_rate,
    1.0 * age_20_24 / age_total AS age_20_24_rate,
    1.0 * age_25_29 / age_total AS age_25_29_rate,
    1.0 * age_30_34 / age_total AS age_30_34_rate,
    1.0 * age_35_39 / age_total AS age_35_39_rate,
    1.0 * age_40_44 / age_total AS age_40_44_rate,
    1.0 * age_45_49 / age_total AS age_45_49_rate,
    1.0 * age_50_54 / age_total AS age_50_54_rate,
    1.0 * age_55_59 / age_total AS age_55_59_rate,
    1.0 * age_60_64 / age_total AS age_60_64_rate,
    1.0 * age_65_69 / age_total AS age_65_69_rate,
    1.0 * age_70_74 / age_total AS age_70_74_rate,
    1.0 * age_75_79 / age_total AS age_75_79_rate,
    1.0 * age_80_84 / age_total AS age_80_84_rate,
    1.0 * age_85_89 / age_total AS age_85_89_rate,
    1.0 * age_90_94 / age_total AS age_90_94_rate,
    1.0 * age_95plus / age_total AS age_95plus_rate

FROM view_age_5year_groups;


-- ============================================================
-- 5歳階級割合：short版
-- ============================================================

DROP VIEW IF EXISTS view_age_5year_short_groups_rate;

CREATE VIEW view_age_5year_short_groups_rate AS

SELECT
    observation_date,
    area_name,
    sex,

    1.0 * age_00_04 / age_total AS age_00_04_rate,
    1.0 * age_05_09 / age_total AS age_05_09_rate,
    1.0 * age_10_14 / age_total AS age_10_14_rate,
    1.0 * age_15_19 / age_total AS age_15_19_rate,
    1.0 * age_20_24 / age_total AS age_20_24_rate,
    1.0 * age_25_29 / age_total AS age_25_29_rate,
    1.0 * age_30_34 / age_total AS age_30_34_rate,
    1.0 * age_35_39 / age_total AS age_35_39_rate,
    1.0 * age_40_44 / age_total AS age_40_44_rate,
    1.0 * age_45_49 / age_total AS age_45_49_rate,
    1.0 * age_50_54 / age_total AS age_50_54_rate,
    1.0 * age_55_59 / age_total AS age_55_59_rate,
    1.0 * age_60_64 / age_total AS age_60_64_rate,
    1.0 * age_65_69 / age_total AS age_65_69_rate,
    1.0 * age_70_74 / age_total AS age_70_74_rate,
    1.0 * age_75_79 / age_total AS age_75_79_rate,
    1.0 * age_80_84 / age_total AS age_80_84_rate,
    1.0 * age_85plus / age_total AS age_85plus_rate

FROM view_age_5year_short_groups;


-- ============================================================
-- 年齢3区分
--
-- short版を使用
-- ============================================================

DROP VIEW IF EXISTS view_three_age_groups_rate;

CREATE VIEW view_three_age_groups_rate AS

SELECT
    observation_date,
    area_name,
    sex,
    age_total,

    -- 年少人口 0-14歳
    age_00_04
        + age_05_09
        + age_10_14
        AS pop_0_14,

    -- 生産年齢人口 15-64歳
    age_15_19
        + age_20_24
        + age_25_29
        + age_30_34
        + age_35_39
        + age_40_44
        + age_45_49
        + age_50_54
        + age_55_59
        + age_60_64
        AS pop_15_64,

    -- 老年人口 65歳以上
    age_65_69
        + age_70_74
        + age_75_79
        + age_80_84
        + age_85plus
        AS pop_65plus,

    -- 年少人口割合
    1.0 * (
        age_00_04
        + age_05_09
        + age_10_14
    ) / age_total
        AS pop_0_14_rate,

    -- 生産年齢人口割合
    1.0 * (
        age_15_19
        + age_20_24
        + age_25_29
        + age_30_34
        + age_35_39
        + age_40_44
        + age_45_49
        + age_50_54
        + age_55_59
        + age_60_64
    ) / age_total
        AS pop_15_64_rate,

    -- 老年人口割合
    1.0 * (
        age_65_69
        + age_70_74
        + age_75_79
        + age_80_84
        + age_85plus
    ) / age_total
        AS pop_65plus_rate

FROM view_age_5year_short_groups;

-- ============================================================
-- Excelレポート出力用データ
--
-- Excelテンプレートの source シートへ出力するためのVIEW
-- ============================================================

DROP VIEW IF EXISTS view_population_data_total;
DROP VIEW IF EXISTS view_excel_report_data;

CREATE VIEW view_excel_report_data AS

SELECT
    -- --------------------------------------------------------
    -- 基本人口
    -- --------------------------------------------------------
    b.observation_date,
    b.area_name,
    b.total_population,
    b.male_population,
    b.female_population,
    b.total_households,

    1.0 * b.total_population / b.total_households
        AS total_household_size,

    -- --------------------------------------------------------
    -- 月次人口増減
    -- --------------------------------------------------------
    mc.monthly_population_change,
    mc.monthly_natural_change,
    mc.births_monthly,
    mc.deaths_monthly,
    mc.monthly_net_migration,

    -- --------------------------------------------------------
    -- 5歳階級：総数
    -- --------------------------------------------------------
    age_t.age_00_04 AS total_age_00_04,
    age_t.age_05_09 AS total_age_05_09,
    age_t.age_10_14 AS total_age_10_14,
    age_t.age_15_19 AS total_age_15_19,
    age_t.age_20_24 AS total_age_20_24,
    age_t.age_25_29 AS total_age_25_29,
    age_t.age_30_34 AS total_age_30_34,
    age_t.age_35_39 AS total_age_35_39,
    age_t.age_40_44 AS total_age_40_44,
    age_t.age_45_49 AS total_age_45_49,
    age_t.age_50_54 AS total_age_50_54,
    age_t.age_55_59 AS total_age_55_59,
    age_t.age_60_64 AS total_age_60_64,
    age_t.age_65_69 AS total_age_65_69,
    age_t.age_70_74 AS total_age_70_74,
    age_t.age_75_79 AS total_age_75_79,
    age_t.age_80_84 AS total_age_80_84,
    age_t.age_85plus AS total_age_85plus,

    -- --------------------------------------------------------
    -- 5歳階級：男性
    -- --------------------------------------------------------
    age_m.age_00_04 AS male_age_00_04,
    age_m.age_05_09 AS male_age_05_09,
    age_m.age_10_14 AS male_age_10_14,
    age_m.age_15_19 AS male_age_15_19,
    age_m.age_20_24 AS male_age_20_24,
    age_m.age_25_29 AS male_age_25_29,
    age_m.age_30_34 AS male_age_30_34,
    age_m.age_35_39 AS male_age_35_39,
    age_m.age_40_44 AS male_age_40_44,
    age_m.age_45_49 AS male_age_45_49,
    age_m.age_50_54 AS male_age_50_54,
    age_m.age_55_59 AS male_age_55_59,
    age_m.age_60_64 AS male_age_60_64,
    age_m.age_65_69 AS male_age_65_69,
    age_m.age_70_74 AS male_age_70_74,
    age_m.age_75_79 AS male_age_75_79,
    age_m.age_80_84 AS male_age_80_84,
    age_m.age_85plus AS male_age_85plus,

    -- --------------------------------------------------------
    -- 5歳階級：女性
    -- --------------------------------------------------------
    age_f.age_00_04 AS female_age_00_04,
    age_f.age_05_09 AS female_age_05_09,
    age_f.age_10_14 AS female_age_10_14,
    age_f.age_15_19 AS female_age_15_19,
    age_f.age_20_24 AS female_age_20_24,
    age_f.age_25_29 AS female_age_25_29,
    age_f.age_30_34 AS female_age_30_34,
    age_f.age_35_39 AS female_age_35_39,
    age_f.age_40_44 AS female_age_40_44,
    age_f.age_45_49 AS female_age_45_49,
    age_f.age_50_54 AS female_age_50_54,
    age_f.age_55_59 AS female_age_55_59,
    age_f.age_60_64 AS female_age_60_64,
    age_f.age_65_69 AS female_age_65_69,
    age_f.age_70_74 AS female_age_70_74,
    age_f.age_75_79 AS female_age_75_79,
    age_f.age_80_84 AS female_age_80_84,
    age_f.age_85plus AS female_age_85plus,

    -- --------------------------------------------------------
    -- 年齢3区分：総数
    -- --------------------------------------------------------
    three_t.pop_0_14 AS total_pop_0_14,
    three_t.pop_15_64 AS total_pop_15_64,
    three_t.pop_65plus AS total_pop_65plus,

    -- --------------------------------------------------------
    -- 年齢3区分：男性
    -- --------------------------------------------------------
    three_m.pop_0_14 AS male_pop_0_14,
    three_m.pop_15_64 AS male_pop_15_64,
    three_m.pop_65plus AS male_pop_65plus,

    -- --------------------------------------------------------
    -- 年齢3区分：女性
    -- --------------------------------------------------------
    three_f.pop_0_14 AS female_pop_0_14,
    three_f.pop_15_64 AS female_pop_15_64,
    three_f.pop_65plus AS female_pop_65plus,

    -- データの由来
    b.source

FROM view_base_data AS b


-- 月次増減
LEFT JOIN view_monthly_change_data AS mc
    ON b.observation_date = mc.observation_date
   AND b.area_name = mc.area_name


-- 5歳階級：総数
LEFT JOIN view_age_5year_short_groups AS age_t
    ON b.observation_date = age_t.observation_date
   AND b.area_name = age_t.area_name
   AND age_t.sex = 'total'


-- 5歳階級：男性
LEFT JOIN view_age_5year_short_groups AS age_m
    ON b.observation_date = age_m.observation_date
   AND b.area_name = age_m.area_name
   AND age_m.sex = 'male'


-- 5歳階級：女性
LEFT JOIN view_age_5year_short_groups AS age_f
    ON b.observation_date = age_f.observation_date
   AND b.area_name = age_f.area_name
   AND age_f.sex = 'female'


-- 年齢3区分：総数
LEFT JOIN view_three_age_groups_rate AS three_t
    ON b.observation_date = three_t.observation_date
   AND b.area_name = three_t.area_name
   AND three_t.sex = 'total'


-- 年齢3区分：男性
LEFT JOIN view_three_age_groups_rate AS three_m
    ON b.observation_date = three_m.observation_date
   AND b.area_name = three_m.area_name
   AND three_m.sex = 'male'


-- 年齢3区分：女性
LEFT JOIN view_three_age_groups_rate AS three_f
    ON b.observation_date = three_f.observation_date
   AND b.area_name = three_f.area_name
   AND three_f.sex = 'female';


