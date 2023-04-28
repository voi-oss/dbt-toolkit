select *
from {{ source('raw', 'city') }}
