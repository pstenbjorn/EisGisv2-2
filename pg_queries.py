QUERIES ={'get_process':"""select distinct u.file_id, file_type, file_name, count(distinct sa.street_address_id) as records,
sum( case when ca.lat != 'not found' then 1 else 0 end)::varchar as geocoded,
sum( case when ca.lat = 'not found' then 1 else 0 end)::varchar as not_geocoded
        from 
        upload_data.uploaded_file u
        left outer join
        upload_data.street_address sa on sa.file_id = u.file_id
        left outer join
        public.census_geocoded_address ca on ca.street_address_id = sa.street_address_id
        where u.processed_date is null and file_type = 'address'
        and u.create_user = '{0}'
        group by u.file_id, file_type, file_name
union
select distinct u.file_id, file_type, file_name, count(distinct d.district_id) as records,
'n/a' as geocoded,
'n/a' as not_geocoded
        from 
        upload_data.uploaded_file u
        left outer join
        upload_data.district d on d.file_id = u.file_id
        where u.processed_date is null and file_type = 'district'
        and u.create_user = '{0}'
        group by u.file_id, file_type, file_name
union
select distinct u.file_id, file_type, file_name, count(distinct d.district_precinct_id) as records,
'n/a' as geocoded,
'n/a' as not_geocoded
        from 
        upload_data.uploaded_file u
        left outer join
        upload_data.district_precinct d on d.file_id = u.file_id
        where u.processed_date is null and file_type = 'precinctdistrict'
        and u.create_user = '{0}'
        group by u.file_id, file_type, file_name
order by file_type"""}