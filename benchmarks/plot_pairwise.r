library(ggplot2)
library(Cairo)
library(RColorBrewer)

plot_pairwise <- function(reference_file, comparison_files) {
    all_data <- data.frame()

    # Read the reference file
    ref_file_name <- basename(reference_file)
    valid_format <- grepl("^results_([a-zA-Z]+)_\\d{4}-\\d{2}-\\d{2}-\\d{2}-\\d{2}\\.csv$", ref_file_name)

    if (!valid_format) {
        stop("The reference file must match the format: result_generator_YYYY-MM-DD-HH-mm.csv")
    }

    ref_generator <- sub("^results_([a-zA-Z]+)_\\d{4}-\\d{2}-\\d{2}-\\d{2}-\\d{2}\\.csv$", "\\1", ref_file_name)
    ref_data <- read.csv(reference_file)

    # Ensure required columns exist in the reference file
    if (!all(c("bucket_num", "cnt", "rel_freq") %in% colnames(ref_data))) {
        stop("The reference CSV file must contain the columns: bucket_num, cnt, rel_freq.")
    }

    ref_data$generator <- ref_generator

    for (file_path in comparison_files) {
        file_name <- basename(file_path)
        valid_format <- grepl("^results_([a-zA-Z]+)_\\d{4}-\\d{2}-\\d{2}-\\d{2}-\\d{2}\\.csv$", file_name)

        if (!valid_format) {
            stop("Each comparison file must match the format: result_generator_YYYY-MM-DD-HH-mm.csv")
        }

        generator <- sub("^results_([a-zA-Z]+)_\\d{4}-\\d{2}-\\d{2}-\\d{2}-\\d{2}\\.csv$", "\\1", file_name)

        data <- read.csv(file_path)

        # Ensure required columns exist
        if (!all(c("bucket_num", "cnt", "rel_freq") %in% colnames(data))) {
            stop("Each comparison CSV file must contain the columns: bucket_num, cnt, rel_freq.")
        }

        data$generator <- generator
        combined_data <- rbind(ref_data, data)

        # Add a new column to identify the pair
        combined_data$pair <- paste(ref_generator, generator, sep = " vs ")

        all_data <- rbind(all_data, combined_data)
    }

    zipfdist <- ggplot(all_data, aes(x = bucket_num, y = rel_freq * 100, color = generator)) +
        geom_line() +
        scale_y_log10() +
        ylab("Accesses [%]") +
        xlab("Histogram Buckets") +
        theme_bw() +
        facet_wrap(~ pair, scales = "free_y") +
        theme(legend.position = "none")

    widthInline <- 8
    heightInline <- 6

    output_file <- "pairwise_graphs.pdf"

    CairoPDF(output_file, width = widthInline, height = heightInline, bg = "transparent")
    print(zipfdist)
    dev.off()

    cat("Pairwise plot saved to:", output_file, "\n")
}

args <- commandArgs(trailingOnly = TRUE)

if (length(args) < 2) {
    stop("Usage: Rscript script.R <reference_csv_file> <comparison_csv_file1> <comparison_csv_file2> ...")
}

# Call the function with the provided file paths
reference_file <- args[1]
comparison_files <- args[-1]
plot_pairwise(reference_file, comparison_files)
