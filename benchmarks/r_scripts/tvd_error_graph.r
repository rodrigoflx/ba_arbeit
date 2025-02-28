library(optparse)
library(jsonlite)
library(ggplot2)
library(dplyr)
library(latex2exp)
library(stringr)
library(scales)

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
  )
)

opt_parser <- OptionParser(option_list = option_list)
opt <- parse_args(opt_parser, positional_arguments = TRUE)

file_path <- opt$args

file_paths <- as.character(file_path)
exponent <- opt$options$skew

df <- data.frame(
  sampler = character(),
  samples = integer(),
  n = integer(),
  tvd = numeric(),
  stringsAsFactors = FALSE
)

for (file in file_paths) {
  sampled_zipf <- read.csv(file)

  samples <- tail(sampled_zipf$entry, n=1)
  n <- sum(sampled_zipf$cnt)
  sampler = str_extract(file, "(?<=/)([^_/]+)(?=(?:_[^/]*)?$)")


  theoretical_zipf <- dzipf(n, samples, as.numeric(exponent))

  tvd <- sum(abs(theoretical_zipf - sampled_zipf$rel_freq)) / 2
  new_row <- data.frame(
    samples=samples,
    sampler=sampler,
    n = n,
    tvd = tvd
  )
  df <- rbind(df, new_row)
}

# Plot TVD against n for each sampler
p <- ggplot(df, aes(x = n, y = tvd, color = sampler, group = sampler)) +
  geom_line() +
  geom_point() +
  labs(
    title = "Total Variation Distance vs. Domain Size",
    x = TeX("n"),
    y = TeX("TVD")
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
ggsave("TVD_vs_n.png", plot = p, width = 8, height = 6)