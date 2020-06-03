library(data.table)

setwd('E:/Documents/gitRep/Meteobike/Calibration')

# example with 10 sensors
sensor_id <- c(
    'sensor_1',
    'sensor_2',
    'sensor_3',
    'sensor_4',
    'sensor_5',
    'sensor_6',
    'sensor_7',
    'sensor_8',
    'sensor_9',
    'sensor_10'
)

# define a timespan with 100 Values
date_start <- lubridate::floor_date(as.POSIXct('2020-06-01 12:21:00'))
date_end <- lubridate::ceiling_date(as.POSIXct('2020-06-01 14:00:00'))
# create a sequence with all daten
date <- seq(date_start, date_end, 'min')

# vector to data.table
data <- data.table(sensor_id)

# initialize empty data.table to append to
all_data <- data.table()
all_dates <- data.table()

# multiply the
i <- 0
while(i < 120) {
    all_data <- rbind(all_data, data)
    i <- i + 1
}

j <- 0

while(j < 12) {
    all_dates <- rbind(all_dates, date)
    j <- j + 1
}

all_data <- all_data[order(rank(sensor_id)), ]

set.seed(4711)
hum_rgs <- round(runif(100, 30, 90), 2)
temp_rgs <- round(runif(100, 5, 29), 2)

all_data <- cbind(temp_rgs, hum_rgs, all_data)

for (sensor in sensor_id) {
    sensor <- toString(sensor)
    hum_coefficient <- runif(1, 0.7, 1.3)
    hum_add <- runif(1, -10, 10)
    temp_coefficient <- runif(1, 0.7, 1.3)
    temp_add <- runif(1, -1.2, 1.2)
    all_data[sensor_id == sensor, hum:= hum_rgs * hum_coefficient + hum_add]
    all_data[sensor_id == sensor, temp:= temp_rgs * temp_coefficient + temp_add]
    all_data[sensor_id == sensor, hum_pre_calib_coef := hum_coefficient]
    all_data[sensor_id == sensor, hum_pre_calib_add := hum_add]
    all_data[sensor_id == sensor, temp_pre_calib_coef := temp_coefficient]
    all_data[sensor_id == sensor, temp_pre_calib_add := temp_add]
    }


randomizer_temp <-runif(1200, -1, 1)
randomizer_hum <-runif(1200, -10, 10)
data <- cbind(all_dates, all_data, randomizer_temp, randomizer_hum)
data[, temp := temp + randomizer_temp]
data[, hum := hum + randomizer_hum]


colnames(data)[1] <- 'date'

fwrite(
    x = data,
    file = 'sample_data.csv',
    dateTimeAs = 'write.csv'
)
