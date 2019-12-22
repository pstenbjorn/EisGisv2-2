QUERIES ={'get_process':"""select 
dt.district_type_name as "DistType", d.district_name as "Dist",
aa.mapped_district_name as "Mapped", count(distinct aa.street_address_id) as "Addresses",
sum(case when aa.matches = true then
    1 else 0 end) as "Matches",
min(dist_from_edge)::decimal(12,4) as "MinKmFromEdge"

from public.audited_addresses aa
inner join upload_data.district_type dt on dt.district_type_id = aa.district_type_id
inner join upload_data.district d on d.district_id = aa.district_id
where aa.create_user = '{0}' and aa.create_date >= now()::date
group by
dt.district_type_name, d.district_name,
aa.mapped_district_name
order by dt.district_type_name, d.district_name,
aa.mapped_district_name"""}