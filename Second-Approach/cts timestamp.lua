-- This function transforms a timestamp into a string
function cts_function(tag, timestamp,record)
   timestamp = tostring(record["cts_timestamp_bin"])
   record["cts_timestamp_bin"] = nil
   return 1, timestamp, record
end


