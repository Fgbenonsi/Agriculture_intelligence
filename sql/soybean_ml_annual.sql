CREATE OR REPLACE VIEW soybean_ml_annual AS
SELECT
    harvested,
    code,
    state,
    county,
    MAX(yield) AS yield,
    MAX(yield_trend) AS yield_trend,
    MAX(yield_trend_corrected) AS yield_trend_corrected,
    SUM(acc_rainfall) AS total_rainfall,
    AVG(mean_tmin) AS avg_tmin,
    AVG(mean_tmax) AS avg_tmax,
    SUM(hot_days) AS total_hot_days,
    SUM(lowrain_days) AS total_lowrain_days,
    AVG(oni) AS avg_oni,
    MAX(soy_area) AS soy_area,
    AVG(mean_ndvi) AS avg_ndvi,
    AVG(mean_evi) AS avg_evi,
    AVG(mean_cvi) AS avg_cvi,
    AVG(mean_gli) AS avg_gli,
    AVG(spi1) AS avg_spi1,
    AVG(spi3) AS avg_spi3,
    AVG(sti1) AS avg_sti1,
    SUM(etp) AS total_etp,
    SUM(def) AS total_def,
    MAX(previous_yield) AS previous_yield
FROM soybean_ml
GROUP BY harvested, code, state, county;


SELECT COUNT(*) FROM soybean_ml_annual;