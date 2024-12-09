library(ggplot2)
library(Cairo)
library(RColorBrewer)

plot_distribution <- function(file_path) {
    file_name <- basename(file_path)
    valid_format <- grepl("^results_([a-zA-Z]+)_\\d{4}-\\d{2}-\\d{2}-\\d{2}-\\d{2}\\.csv$", file_name)
  
    if (!valid_format) {
        stop("The input file must match the format: result_generator_YYYY-MM-DD-HH-mm.csv")
    }
  
    generator <- sub("^results_([a-zA-Z]+)_\\d{4}-\\d{2}-\\d{2}-\\d{2}-\\d{2}\\.csv$", "\\1", file_name)


    data <- read.csv(file_path)

    # Ensure required columns exist
    if (!all(c("bucket_num", "cnt", "rel_freq") %in% colnames(data))) {
    stop("The input CSV file must contain the columns: bucket_num, cnt, rel_freq.")
    }

    palette_colors <- brewer.pal(n = 4, name = "Set1")[1]
    zipfdist <- ggplot(data, aes(x = bucket_num, y = rel_freq)) +
        geom_line(color = palette_colors) +
        scale_y_log10() +
        ylab("Acesses [%]") +
        xlab("Histogram Buckets") +
        theme_bw() +
        theme(legend.position = "none")

    output_file <- sprintf("graph_%s.pdf", generator)

    widthInline <- 2.7
    heightInline <- 1.8
    CairoPDF(output_file, width = widthInline, height = heightInline, bg = "transparent")
    print(zipfdist)
    dev.off()

    cat("Plot saved to:", output_file, "\n")
}

args <- commandArgs(trailingOnly = TRUE)

if (length(args) < 1) {
  stop("Usage: Rscript script.R <csv_file>")
}

# Call the function with the provided file path
plot_distribution(args[1])
