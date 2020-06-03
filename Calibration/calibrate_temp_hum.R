library(data.table)
library(ggplot2)


setwd('E:/Documents/gitRep/Meteobike/Calibration')

data <- fread(input = 'sample_data.csv')

data$date <- as.POSIXct(data$date)
data$sensor_id <- as.factor(data$sensor_id)

RMSE <- function(residuals) {
    sqrt(mean(residuals^2, na.rm = T))
}

results <- data.table()

for (sensor in levels(data$sensor_id)) {
    tmp_results <- data.table()
    lin_mod <- lm(data[sensor_id == sensor, temp] ~ data[sensor_id == sensor, temp_rgs])
    slope <- round(x = lin_mod$coefficients[2], 5)
    y_inter <- round(x = lin_mod$coefficients[1], digits = 5)
    rmse <- RMSE(lin_mod$residuals)
    rsq <- summary(lin_mod)$r.squared
    fml <- paste('y = ', slope, 'x + ', y_inter, sep = '')
    temp_cal_a1 <- 1/slope
    temp_cal_a0 <- y_inter
    tmp_results <- cbind(tmp_results, sensor, slope, y_inter, rmse, rsq, fml, temp_cal_a1, temp_cal_a0)
    results_temp <- rbind(results, tmp_results)

    # plot
    plot <- ggplot(data = data[sensor_id == sensor, temp_rgs, temp],
                   aes(x = temp_rgs, y = temp)) +
        geom_point() +
        geom_line(aes(x = temp_rgs,
                      y = temp_rgs,
                      col = 'compared to RGS2'),
                  lwd = 1) +
        scale_y_continuous(name = 'temperature of DHT22-sensor [°C]') +
        scale_x_continuous(name = 'temperature of RGS2 [°C]') +
        labs(title = paste('DHT22-sensor', ' "', sensor, '" ', 'compared to measurements of RGS2', sep = '')) +
        geom_text(aes(y = 28,
                      x = 6,
                      label = paste('RMSE = ',
                                    format(rmse,
                                           digits = 3),
                                    ' K\nR² = ',
                                    format(rsq,
                                           digits = 3),
                                    '\n', fml,
                                    '\nN = ',
                                    nrow(all_data[sensor_id == sensor, ]),
                                    sep = '')),
                  hjust = 0,
                  vjust = 1,
                  fontface = 'italic') +
        theme_bw(base_size = 14) +
        theme(legend.position = 'bottom',
              legend.title = element_blank()) +
        coord_cartesian(xlim = c(5, 29),
                        ylim = c(5, 29),
                        expand = F)

    # apply calibrartion
    data[sensor_id == sensor, temp_calib := (temp / slope) - y_inter]
    # standard deviation

    plot_calib <- ggplot(data = data[sensor_id == sensor, temp_rgs, temp_calib],
                   aes(x = temp_rgs, y = temp_calib)) +
        geom_point() +
        geom_line(aes(x = temp_rgs,
                      y = temp_rgs,
                      col = 'compared to RGS2'),
                  lwd = 1) +
        scale_y_continuous(name = 'temperature of DHT22-sensor [°C]') +
        scale_x_continuous(name = 'temperature of RGS2 [°C]') +
        labs(title = paste('DHT22-sensor', ' "', sensor, '" ', 'compared to measurements of RGS2 after applying calibration', sep = '')) +
        geom_text(aes(y = 28,
                      x = 6,
                      label = paste('RMSE = ',
                                    format(rmse,
                                           digits = 3),
                                    ' K\nR² = ',
                                    format(rsq,
                                           digits = 3),
                                    '\nN = ',
                                    nrow(all_data[sensor_id == sensor, ]),
                                    sep = '')),
                  hjust = 0,
                  vjust = 1,
                  fontface = 'italic') +
        theme_bw(base_size = 14) +
        theme(legend.position = 'bottom',
              legend.title = element_blank()) +
        coord_cartesian(xlim = c(5, 29),
                        ylim = c(5, 29),
                        expand = F)

    ggsave(plot = plot,
           filename = paste(sensor, '_tempcor_plot.png', sep = ''),
           device = 'png',
           scale = 1.8,
           width = 15,
           height = 15,
           units = 'cm',
           dpi = 600)
    ggsave(plot = plot_calib,
           filename = paste(sensor, '_tempcor_plot_calib.png', sep = ''),
           device = 'png',
           scale = 1.8,
           width = 15,
           height = 15,
           units = 'cm',
           dpi = 600)
}

fwrite(x = results_temp,
       file = 'temp_calibration_results.csv')
