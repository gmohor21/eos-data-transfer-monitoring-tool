function parse(str)
  kv = {}
  for key, val in str:gmatch('([^=]+)=([^&]*)[&]?') do
    if key == 'sec.app' and val == '' then
    	val = 'None'
    elseif key ~= 'fxid' then
        val = tonumber(val) or val
    end
     
    kv[key] = val
     
  end
  return kv 
end

function kv_parser(tag, timestamp, record)
   kv = parse(record["raw"])
   if not kv or next(kv) == nil then -- kv is null
      return -1,0,0
   end
   timestamp = tonumber(string.format("%d.%03d",kv.ots or kv.del_ts,kv.otms or kv.del_tns/1e6)) -- make sure otms and del_tns have the 3 digits
   return 2, timestamp, kv
end


