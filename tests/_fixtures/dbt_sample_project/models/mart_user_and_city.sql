select
    _user.id as user_id,
    _user.name as name, -- ambiguous (city also has a name) on purpose
    city.id as city_id

from {{ ref('stg_user') }} as _user

left join {{ ref('stg_city' )}} as city
    on _user.city_id = city.id
