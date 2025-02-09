SELECT prov, provincia, COUNT(*) AS total_registros
FROM ENDI.f1_personas
GROUP BY prov, provincia
ORDER BY prov ASC;

SELECT DISTINCT(prov) FROM ENDI.f1_personas ORDER BY prov;