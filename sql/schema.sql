-- ===========================================================
-- Osaka Population Database
-- schema.sql
-- ===========================================================
BEGIN TRANSACTION;
--- ファイルで一つのトランザクションにする
--- 失敗時のロールバックは呼出側に依存

-- ============================================
-- 国勢調査
-- ============================================

CREATE TABLE IF NOT EXISTS census (
    area_name                  TEXT    NOT NULL,
    total_population           INTEGER,
    male_population            INTEGER,
    female_population          INTEGER,

    population_change          INTEGER,
    population_change_rate     REAL,

    total_households           INTEGER,
    general_households         INTEGER,
    general_household_members  INTEGER,
    general_household_size     REAL,

    population_density         REAL,

    observation_date           TEXT    NOT NULL,

    PRIMARY KEY (area_name, observation_date)
);


-- ============================================
-- 推計人口
-- ============================================

CREATE TABLE IF NOT EXISTS suikei (
    area_name                  TEXT    NOT NULL,
    total_households           INTEGER,
    total_population           INTEGER,
    male_population            INTEGER,
    female_population          INTEGER,

    -- 1年間の増減
    annual_population_change   INTEGER,
    annual_natural_change      INTEGER,
    births_per_year            INTEGER,
    deaths_per_year            INTEGER,
    annual_net_migration       INTEGER,

    -- 1か月間の増減
    monthly_population_change  INTEGER,
    monthly_natural_change     INTEGER,
    births_monthly             INTEGER,
    deaths_monthly             INTEGER,
    monthly_net_migration      INTEGER,

    -- その他
    total_household_size       REAL,
    population_density         REAL,

    observation_date           TEXT    NOT NULL,

    PRIMARY KEY (area_name, observation_date)
);


-- ============================================
-- 補正人口
-- ============================================

CREATE TABLE IF NOT EXISTS hosei (
    area_name          TEXT    NOT NULL,
    total_households   INTEGER,
    total_population   INTEGER,
    male_population    INTEGER,
    female_population  INTEGER,

    observation_date   TEXT    NOT NULL,

    PRIMARY KEY (area_name, observation_date)
);

-- =============================================
-- 5歳階級人口 V001
-- 最上位階級：85歳以上
-- =============================================

CREATE TABLE IF NOT EXISTS population_age5_v001 (
    area_name          TEXT    NOT NULL,
    observation_date   TEXT    NOT NULL,
    sex                TEXT    NOT NULL,

    age_total          INTEGER,
    age_00_04          INTEGER,
    age_05_09          INTEGER,
    age_10_14          INTEGER,
    age_15_19          INTEGER,
    age_20_24          INTEGER,
    age_25_29          INTEGER,
    age_30_34          INTEGER,
    age_35_39          INTEGER,
    age_40_44          INTEGER,
    age_45_49          INTEGER,
    age_50_54          INTEGER,
    age_55_59          INTEGER,
    age_60_64          INTEGER,
    age_65_69          INTEGER,
    age_70_74          INTEGER,
    age_75_79          INTEGER,
    age_80_84          INTEGER,
    age_85plus         INTEGER,

    PRIMARY KEY (
        area_name,
        observation_date,
        sex
    ),

    CHECK (sex IN ('total', 'male', 'female'))
);


-- =============================================
-- 5歳階級人口 V002
-- 最上位階級：95歳以上
-- =============================================

CREATE TABLE IF NOT EXISTS population_age5_v002 (
    area_name          TEXT    NOT NULL,
    observation_date   TEXT    NOT NULL,
    sex                TEXT    NOT NULL,

    age_total          INTEGER,
    age_00_04          INTEGER,
    age_05_09          INTEGER,
    age_10_14          INTEGER,
    age_15_19          INTEGER,
    age_20_24          INTEGER,
    age_25_29          INTEGER,
    age_30_34          INTEGER,
    age_35_39          INTEGER,
    age_40_44          INTEGER,
    age_45_49          INTEGER,
    age_50_54          INTEGER,
    age_55_59          INTEGER,
    age_60_64          INTEGER,
    age_65_69          INTEGER,
    age_70_74          INTEGER,
    age_75_79          INTEGER,
    age_80_84          INTEGER,
    age_85_89          INTEGER,
    age_90_94          INTEGER,
    age_95plus         INTEGER,

    PRIMARY KEY (
        area_name,
        observation_date,
        sex
    ),

    CHECK (sex IN ('total', 'male', 'female'))
);

COMMIT;
