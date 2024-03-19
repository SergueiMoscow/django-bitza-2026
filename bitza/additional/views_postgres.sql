CREATE OR REPLACE VIEW expected_payments AS
SELECT
    cast(random()*1000000000 as integer) as id,
    contracts.number,
    to_char(contracts.date_begin, 'DD.MM.YYYY') as date_begin,
    contracts.room_id AS room,
    contracts.price,
    sum(payments.total) AS payed,
    age(current_date, contracts.date_begin) as diff,
ROUND(
    (
        EXTRACT(YEARS FROM AGE(now(), contracts.date_begin)) * 12 +
        EXTRACT(MONTH FROM AGE(now(), contracts.date_begin)) +
        EXTRACT(DAY FROM AGE(now(), contracts.date_begin)) / 30.0
    ),
    1
    ) AS month_diff,
    round(coalesce(sum(payments.total) / contracts.price, 0), 1) as paid_months,
    ROUND(
    (
        EXTRACT(YEAR FROM AGE(now(), contracts.date_begin)) * 12 +
        EXTRACT(MONTH FROM AGE(now(), contracts.date_begin)) +
        EXTRACT(DAY FROM AGE(now(), contracts.date_begin)) / 30.0 -
        COALESCE(SUM(payments.total) / contracts.price, 0)
    ),
    1
    ) AS debt_month,
    ROUND(
    (
        EXTRACT(YEAR FROM AGE(now(), contracts.date_begin)) * 12 +
        EXTRACT(MONTH FROM AGE(now(), contracts.date_begin)) +
        EXTRACT(DAY FROM AGE(now(), contracts.date_begin)) / 30.0 -
        COALESCE(SUM(payments.total) / contracts.price, 0)
    ),
    1
    ) * contracts.price AS debt_rur,
    MAX(payments.date) AS last_payment_date
from
    rent_contract as contracts
    left join rent_payment as payments on contracts.number = payments.contract_id
where
    contracts.status = 'A'
group by
    contracts.number
order by
    debt_rur desc;


CREATE OR REPLACE VIEW vacant_rooms AS
    SELECT rent_room.shortname AS shortname
    FROM rent_room
    WHERE (
        rent_room.status = 'A'
        AND (
            NOT (rent_room.shortname IN (
                SELECT rent_contract.room_id FROM rent_contract WHERE rent_contract.status = 'A'
            )
            )
        )
    );
