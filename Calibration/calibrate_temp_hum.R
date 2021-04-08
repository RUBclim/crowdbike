library(data.table)
library(ggplot2)
library(openair)

setwd('E:/Documents/gitRep/Meteobike/Calibration/')

file_list <- list.files(
    'data',
    full.names = T,
    pattern = '^calibration_measurements_*')

data_list <- lapply(file_list, fread)
data <- rbindlist(data_list)

# convert date to posix
data$date <- as.POSIXct(data$date, tz = 'UTC')

data_rgs <- fread('data/data_rgsII.csv', skip = 4)
data_rgs <- data_rgs[, c('V1', 'V9', 'V8')]
colnames(data_rgs) <- c('date', 'temp', 'hum')
data_rgs$date <- as.POSIXct(
    data_rgs$date,
    format = '%d/%m/%Y %H:%M',
    tz = 'Etc/GMT-1'
)

# shift timezone to UTC
attr(data_rgs$date, "tzone") <- "UTC"

# remove totally wrong values ----
# temperature
data[temp > 30, temp := NA]
data[temp < 5, temp := NA]

# humidity
data[hum > 150, temp := NA]
data[hum < -10, temp := NA]


RMSE <- function(residuals) {
    sqrt(mean(residuals^2, na.rm = T))
}


plot_uncalibrated <- function(data, results, param) {
    if (param == 'temp') {
        x <- data$temp_rgs
        y <- data$temp_dht
        name_x <- 'temperature of RGS II [°C]'
        name_y <- 'temperature of DHT22-sensor [°C]'
        lim <- c(5, 30)
        text_y <- 28
        text_x <- 6
        unit <- ' K'
    }
    else if (param == 'hum') {
        x <- data$hum_rgs
        y <- data$hum_dht
        name_x <- 'rel. humidity of RGS II [%]'
        name_y <- 'rel. humidity of DHT22-sensor [%]'
        lim <- c(0, 100)
        text_y <- 90
        text_x <- 5
        unit <- ' %'
    }
    else {
        stop(
            paste(
                '"param" must be either "temp" or "hum" not ',
                param, sep = ''
            )
        )
    }
    ggplot(data = data, aes(x = x , y = y)) +
        geom_point() +
        geom_abline(intercept = 0, slope = 1, color = 'red', lwd = 1) +
        scale_x_continuous(name = name_x) +
        scale_y_continuous(name = name_y) +
        labs(
            title = paste(
                'DHT22-sensor "', factor(data$sensor_id),
                '" compared to measurements of RGS II',
                sep = ''
            )
        ) +
        geom_text(
            aes(
                y = text_y,
                x = text_x,
                label = paste(
                    'RMSE = ',
                    format(results$rmse, digits = 3),
                    unit,' \nR² = ',
                    format(results$rsq, digits = 3),
                    '\n', results$fml,
                    '\nN = ',
                    (nrow(na.omit(data))),
                    sep = ''
                )
            ),
            hjust = 0,
            vjust = 1,
            fontface = 'italic'
        ) +
        theme_bw(base_size = 14) +
        coord_cartesian(
            xlim = lim,
            ylim = lim,
            expand = F
        )
}


plot_calibrated <- function(data, results, param) {
    if (param == 'temp') {
        x <- data$temp_rgs
        y <- data$temp_calib
        name_x <- 'temperature of RGS II [°C]'
        name_y <- 'temperature of DHT22-sensor [°C]'
        lim <- c(5, 30)
        text_y <- 28
        text_x <- 6
        unit <- ' K'
    }
    else if (param == 'hum') {
        x <- data$hum_rgs
        y <- data$hum_calib
        name_x <- 'rel. humidity of RGS II [%]'
        name_y <- 'rel. humidity of DHT22-sensor [%]'
        lim <- c(0, 100)
        text_y <- 90
        text_x <- 5
        unit <- ' %'
    }
    else {
        stop(
            paste(
                '"param" must be either "temp" or "hum" not ',
                param,
                sep = ''
            )
        )
    }
    ggplot(data = data, aes(x = x , y = y)) +
        geom_point() +
        geom_abline(intercept = 0, slope = 1, color = 'red', lwd = 1) +
        scale_y_continuous(name = name_y) +
        scale_x_continuous(name = name_x) +
        labs(
            title = paste(
                'DHT22-sensor "',
                factor(data$sensor_id),
                '" compared to measurements of RGS II after calibration',
                sep = ''
            )
        ) +
        geom_text(
            aes(
                y = text_y,
                x = text_x,
                label = paste(
                    'RMSE = ',
                    format(results$rmse, digits = 3),
                    unit, ' \nR² = ',
                    format(results$rsq, digits = 3),
                    '\nN = ',
                    (nrow(na.omit(data))),
                    sep = ''
                )
            ),
            hjust = 0,
            vjust = 1,
            fontface = 'italic'
        ) +
        theme_bw(base_size = 14) +
        coord_cartesian(
            xlim = lim,
            ylim = lim,
            expand = F
        )
}

calibrate <- function(data, sensor, rgs_data, start, param) {
    data <- data[date >= as.POSIXct(start, tz = 'UTC'), ]
    data_10_min <- timeAverage(
        mydata = data[sensor_id == sensor, ],
        avg.time = '10 min',
        statistic = 'mean',
        fill = T,
        start.date = start,
        type = 'sensor_id'
    )

    data_10_min <- as.data.table(data_10_min)
    if (sum(is.na(data_10_min)) == nrow(data_10_min)) {
        stop('the data only contains NA values')
    }

    data_rgs <- rgs_data
    # join both tables together
    setkey(data_10_min, date)
    setkey(data_rgs, date)

    all_data <- merge(x = data_10_min, y = data_rgs, all.x = T)

    colnames(all_data) <- c(
        'date',
        'sensor_id',
        'temp_dht',
        'hum_dht',
        'temp_rgs',
        'hum_rgs'
    )

    # generate linear model of data
    if (param == 'temp') {
        lin_mod <- lm(
            all_data[sensor_id == sensor, temp_dht]
                      ~ all_data[sensor_id == sensor, temp_rgs])
    } else if (param == 'hum') {
        lin_mod <- lm(all_data[sensor_id == sensor, hum_dht]
                      ~ all_data[sensor_id == sensor, hum_rgs])
    } else {
        stop(
            paste(
                '"param" must be either "temp" or "hum" not ',
                param,
                sep = ''
            )
        )
    }

    slope <- round(x = lin_mod$coefficients[2], 5)
    y_inter <- round(x = lin_mod$coefficients[1], digits = 5)
    rmse <- RMSE(lin_mod$residuals)
    rsq <- summary(lin_mod)$r.squared
    fml <- paste('y = ', slope, 'x + ', y_inter, sep = '')
    if (param == 'temp') {
        temp_cal_a1 <- slope
        temp_cal_a0 <- y_inter
        results <- data.table(
            sensor,
            slope,
            y_inter,
            rmse,
            rsq,
            fml,
            temp_cal_a1,
            temp_cal_a0
        )
    } else {
        hum_cal_a1 <- slope
        hum_cal_a0 <- y_inter
        results <- data.table(
            sensor,
            slope,
            y_inter,
            rmse,
            rsq,
            fml,
            hum_cal_a1,
            hum_cal_a0
        )
    }

    all_data$sensor_id <- as.factor(all_data$sensor_id)

    # apply calibration
    if (param == 'temp') {
        plot_uncalib <- plot_uncalibrated(
            data = all_data, results = results, param = 'temp')
        all_data[, 'temp_calib' := (temp_dht / slope) - y_inter]
        plot_calib <- plot_calibrated(
            data = all_data, results = results, param = 'temp')
    } else {
        plot_uncalib <- plot_uncalibrated(
            data = all_data, results = results, param = 'hum')
        all_data[, 'hum_calib' := (hum_dht / slope) - y_inter]
        plot_calib <- plot_calibrated(
            data = all_data, results = results, param = 'hum')
    }

    return(
        list(
            'results' = results,
            'plot_uncalib' = plot_uncalib,
            'plot_calib' = plot_calib
        )
    )
}


save_plot <- function(plot, prefix, trailing) {
    ggsave(plot = plot,
           filename = paste(prefix, '_', trailing, '.png', sep = ''),
           device = 'png',
           scale = 1.8,
           width = 14,
           height = 14,
           units = 'cm',
           dpi = 600)
}


data$sensor_id <- as.factor(data$sensor_id)

calib_table_temp <- data.table()
calib_table_hum <- data.table()

for (sensor_id in levels(data$sensor_id)) {
    cat(paste('\ncalculating calibration for sensor:', sensor_id, '\n'))

    result_temp <- calibrate(
        data = data,
        sensor = sensor_id,
        rgs_data = data_rgs,
        start = '2020-06-01 15:20:00',
        param = 'temp'
    )

    result_hum <- calibrate(
        data = data,
        sensor = sensor_id,
        rgs_data = data_rgs,
        start = '2020-06-01 15:20:00',
        param = 'hum'
    )


    save_plot(
        plot = result_temp$plot_uncalib,
        prefix = result_temp$results$sensor,
        trailing = 'tempcor_plot'
    )

    save_plot(
        plot = result_temp$plot_calib,
        prefix = result_temp$results$sensor,
        trailing = 'tempcor_plot_calib'
    )

    calib_table_temp <- rbind(calib_table_temp, result_temp$results)


    save_plot(
        plot = result_hum$plot_uncalib,
        prefix = result_hum$results$sensor,
        trailing = 'humcor_plot'
    )

    save_plot(
        plot = result_hum$plot_calib,
        prefix = result_hum$results$sensor,
        trailing = 'humcor_plot_calib'
    )

    calib_table_hum <- rbind(calib_table_hum, result_hum$results)
}

fwrite(x = calib_table_temp, file = 'temp_calibration_results.csv')
fwrite(x = calib_table_hum, file = 'hum_calibration_results.csv')

# lint
source('.lint.R')
lint_my_script('calibrate_temp_hum.R')
