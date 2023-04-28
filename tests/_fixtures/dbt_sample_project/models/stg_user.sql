select *
from {{ source('raw', 'user') }}
