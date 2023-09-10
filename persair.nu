source env.nu

# Check if the response json from the PurpleAir API contains
# a 'false' status. If so, quit, showing the response and
# an error message.
def response_checkForError [
    response: record	# The response from the remote API call.
] {
    if not $response.status {
    	print $response
    	print $response.response
    	let span = (metadata $response).span
      	error make {
    	    msg: "Error in communicating with purple air API",
    	    label: {
    	        text: "origin",
    		start: $span.start
    		end: $span.end
    	    }
    	}
    }
    $response
}

# The interface/call to the persair app that communicates with
# the PurpleAir API to get sensor data for a given sensor.
def persair_sensorDataGet [
    idx:int	# The index of the sensor in the purpleair DB.
] {
    (response_checkForError (persair --sensorDataGet $idx | from json))
}

# The interface/call to the persair app that communicates with
# the PurpleAir API to get the list of sensors in a group.
def persair_sensorsInGroupList [
    group:int	# The ID of the sensor group in the purpleair DB.
] {
    (response_checkForError (
        persair --sensorsInGroupList --usingGroupID $group | from json)
    )
}

# Convenience function to get sensor data
def sensor_dataGet [
    idx:int # The index of the sensor
] {
    persair_sensorDataGet $idx
}

# Get the date a given sensor most recently checked in with purpleair
def sensor_lastSeen [
    idx:int 	# The index of the sensor in the purpleair DB.
] {
    let timelast = (
        [( (persair_sensorDataGet $idx) |
            get response                |
            get sensor                  |
            get last_seen) 1000000000]  |
            math product | into datetime
    )
    return $timelast
}

# Get the list all sensors in a PurpleAir API group
def sensorsInGroup_list [
    group:int	# The group ID
] {
    let sensors = (
        (persair_sensorsInGroupList $group) |
        get response                        |
        get members
    )
    return $sensors
}

# Determine the number of days since a sensor was last seen
def sensor_daysLastSeen [
    idx:int 	# The sensor index to query
] {
    let dist = (
        (date now) - (sensor_lastSeen $idx)     |
        format duration day                     |
        parse '{days} {unit}'                   |
        get days                                |
        into decimal
    )
    return ($dist.0)
}

# Generate a list for all sensors in a group with the number
# of days last seen
def sensorsInGroup_daysLastSeen [
    group:int	# The group ID
] {
    sensorsInGroup_list $group| get sensor_index | each {
        |it| [
            [sensor last_seen];
            [   ($"($it)" | fill -a right -c ' ' -w 10)
                (sensor_daysLastSeen $it)
            ]
        ]
    } | flatten
}

# Return a true/false on a sensor index given a day count.
# If true, the sensor has not checked in since the last day count
# If false, the sensor has checked in
def sensor_wasLastSeen_moreThanDaysAgo [
    idx:int,	# Sensor index
    days:float	# days ago cutoff
] {
    if (sensor_daysLastSeen $idx) > $days {
        return true
    } else {
    	return false
    }
}

# Generate a list of all sensors in a group last seen more than
# a certain number of days ago.
def sensorsInGroup_daysLastSeen_moreThan [
    group:int	# The group ID
    days:float  # how many days
] {
    sensorsInGroup_daysLastSeen $group | where last_seen > $days
}

