library(ggplot2)
library(Cairo)
library(RColorBrewer)
library(glue)
library(optparse)

plot_distributions <- function(file_paths, skew, samples, n) {
  all_data <- data.frame()

  for (file_path in file_paths) {
    file_name <- basename(file_path)
    pattern <- "^([a-zA-Z]+)_\\d{4}-\\d{2}-\\d{2}-\\d{2}-\\d{2}\\.csv$"
    valid_format <- grepl(pattern, file_name)

    if (!valid_format) {
      stop(paste("Each input file must match the format:",
                "result_generator_YYYY-MM-DD-HH-mm.csv"))
    }

    generator <- sub(pattern, "\\1", file_name)
    data <- read.csv(file_path)

    # Ensure required columns exist
    required_cols <- c("entry", "cnt", "rel_freq")
    if (!all(required_cols %in% colnames(data))) {
      stop("The input CSV file must contain the columns: entry, cnt, rel_freq.")
    }

    data$generator <- generator
    all_data <- rbind(all_data, data)
  }

  # Filter out the last bucket (entry == 1000)
  all_data <- all_data[all_data$entry != 1000, ]
  
  zipfdist <- ggplot(all_data, 
                     aes(x = .data$entry, 
                         y = .data$rel_freq * 100, 
                         color = generator)) +
    geom_line() +
    scale_y_log10() +
    ylab("Accesses [%]") +
    xlab("Histogram Buckets") +
    labs(
      caption = glue("Skew {skew}, Samples {samples}, Domain {n}")
    ) +
    theme_bw() +
    facet_wrap(~ generator, scales = "free_y") +
    theme(legend.position = "none")

  output_file <- file.path("graphs", "faceted_graphs.pdf")

  width_inline <- 8
  height_inline <- 6
  CairoPDF(output_file, 
           width = width_inline, 
           height = height_inline, 
           bg = "transparent")
  print(zipfdist)
  dev.off()

  cat("Faceted plot saved to:", output_file, "\n")
}

option_list <- list(
  make_option(
    c("--n"),
    type = "integer",
    help = "Number of elements",
    metavar = "int"
  ),
  make_option(
    c("--samples"),
    type = "integer",
    help = "Number of samples",
    metavar = "int"),
  make_option(
    c("--skew"),
    type = "double",
    help = "Skew factor",
    metavar = "float"
  )
)

# Parse command-line arguments
opt_parser <- OptionParser(option_list = option_list)
opt <- parse_args(opt_parser, positional_arguments = TRUE)

# Extract the arguments
n <- opt$options$n
samples <- opt$options$samples
skew <- opt$options$skew
file_paths <- opt$args

file_paths <- as.character(file_paths)

print(file_paths)

# Call the function with the provided arguments
plot_distributions(file_paths, skew, samples, n)