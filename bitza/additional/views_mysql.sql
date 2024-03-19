-- django_bitza.expected_payments source

CREATE OR REPLACE
ALGORITHM = UNDEFINED VIEW `expected_payments` AS
select
    uuid() AS `id`,
    `contracts`.`number` AS `number`,
    date_format(`contracts`.`date_begin`, '%d.%m.%Y') AS `date_begin`,
    `contracts`.`room_id` AS `room`,
    `contracts`.`price` AS `price`,
    sum(`payments`.`total`) AS `payed`,
    (to_days(now()) - to_days(`contracts`.`date_begin`)) AS `diff`,
    round(((to_days(now()) - to_days(`contracts`.`date_begin`)) / (365 / 12)), 1) AS `month_diff`,
    round(coalesce((sum(`payments`.`total`) / `contracts`.`price`), 0), 1) AS `paid_months`,
    round((((to_days(now()) - to_days(`contracts`.`date_begin`)) / (365 / 12)) - coalesce((sum(`payments`.`total`) / `contracts`.`price`), 0)), 1) AS `debt_month`,
    round(((((to_days(now()) - to_days(`contracts`.`date_begin`)) / (365 / 12)) - coalesce((sum(`payments`.`total`) / `contracts`.`price`), 0)) * `contracts`.`price`), 0) AS `debt_rur`
from
    (`rent_contract` `contracts`
left join `rent_payment` `payments` on
    ((`contracts`.`number` = `payments`.`contract_id`)))
where
    (`contracts`.`status` = 'A')
group by
    `contracts`.`number`
order by
    `debt_rur` desc;


-- a0293853_bitza23.freeRooms source

CREATE OR REPLACE VIEW `vacant_rooms` AS
SELECT
    `rent_room`.`shortname` AS `shortname`
FROM
    `rent_room`
WHERE
    ((`rent_room`.`status` = 'A')
        AND (NOT(`rent_room`.`shortname` IN (
        SELECT
            `rent_contract`.`room_id`
        FROM
            `rent_contract`
        WHERE
            (`rent_contract`.`status` = 'A')))));