library(ggplot2)
library(Cairo)
library(RColorBrewer)

plot_distributions <- function(file_paths) {
    all_data <- data.frame()

    for (file_path in file_paths) {
        file_name <- basename(file_path)
        valid_format <- grepl("^results_([a-zA-Z]+)_\\d{4}-\\d{2}-\\d{2}-\\d{2}-\\d{2}\\.csv$", file_name)

        if (!valid_format) {
            stop("Each input file must match the format: result_generator_YYYY-MM-DD-HH-mm.csv")
        }

        generator <- sub("^results_([a-zA-Z]+)_\\d{4}-\\d{2}-\\d{2}-\\d{2}-\\d{2}\\.csv$", "\\1", file_name)

        data <- read.csv(file_path)

        # Ensure required columns exist
        if (!all(c("bucket_num", "cnt", "rel_freq") %in% colnames(data))) {
            stop("The input CSV file must contain the columns: bucket_num, cnt, rel_freq.")
        }

        data$generator <- generator
        all_data <- rbind(all_data, data)
    }

    palette_colors <- brewer.pal(n = 4, name = "Set1")[1]
    zipfdist <- ggplot(all_data, aes(x = bucket_num, y = rel_freq * 100, color = generator)) +
        geom_line() +
        scale_y_log10() +
        ylab("Accesses [%]") +
        xlab("Histogram Buckets") +
        theme_bw() +
        facet_wrap(~ generator, scales = "free_y") +
        theme(legend.position = "none")

    output_file <- "faceted_graphs.pdf"

    widthInline <- 8
    heightInline <- 6
    CairoPDF(output_file, width = widthInline, height = heightInline, bg = "transparent")
    print(zipfdist)
    dev.off()

    cat("Faceted plot saved to:", output_file, "\n")
}

args <- commandArgs(trailingOnly = TRUE)

if (length(args) < 1) {
    stop("Usage: Rscript script.R <csv_file1> <csv_file2> ...")
}

# Call the function with the provided file paths
plot_distributions(args)
