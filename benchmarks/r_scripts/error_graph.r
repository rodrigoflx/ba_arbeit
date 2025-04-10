library(optparse)
library(jsonlite)
library(ggplot2)
library(dplyr)
library(latex2exp)
library(stringr)
library(scales)
library(glue)
library(readr)

dzipf <- function(rank, total_counts, exponent = 1) {
  zipf_denominator <- sum(1 / (1:total_counts)^exponent)
  return(1 / ((rank)^exponent * zipf_denominator))
}

theme_set(theme_bw())

option_list <- list(
  make_option(
    c("--skew"),
    type = "numeric",
    help = "Skew of Dist",
    metavar = "float"
  ),
  make_option(
    c("--generator", "-g"),
    type = "character",
    help = "Generator (such as YCSB, Rejection, etc.)"
  ),
  make_option(
    c("--output", "-o"),
    type = "character",
    help = "Output file path",
  ),
  make_option(
    c("--n", "-n"),
    type = "integer",
    help = "Support size of the distribution"
  )
)

opt_parser <- OptionParser(option_list = option_list)
opt <- parse_args(opt_parser, positional_arguments = TRUE)

file_path <- opt$args
file_paths <- as.character(file_path)

exponent <- opt$options$skew
sampler <- opt$options$generator
n <- opt$options$n
output <- opt$options$output

df <- read_csv(file_path)

p <- ggplot(df, aes(x = samples, y = tvd)) +
  geom_line() +
  geom_point() +
  scale_x_log10(
    breaks = scales::trans_breaks("log10", function(x) 10^x),
    labels = scales::trans_format("log10", scales::math_format(10^.x))
  ) +
  ylim(0.0,0.6) +
  labs(
    x = TeX("Samples taken"),
    y = TeX("Total Variation Distance")
  ) +
  theme(
    axis.title.x = element_text(margin = margin(t = 10), size = 12),
    axis.title.y = element_text(margin = margin(t = 10), size = 12),
    plot.title = element_text(face = "bold",
                              size = 14,
                              hjust = 0.5,
                              margin = margin(10, 0, 10, 0)),
  )

# Optionally, save the plot to a file
ggsave(output, plot = p, width = 8, height = 6)