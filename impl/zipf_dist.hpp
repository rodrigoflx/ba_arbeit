#ifndef ZIPF_DIST_HPP
#define ZIPF_DIST_HPP

class zipf_dist {
    public:
        zipf_dist() = default;
        double pmf(double k, double a, long n);
        void set_harmonic(double a, long n);
        static double _generate_harmonic(double a, long n);
    private:
        double H_n;
        static double _generate_harmonic_leq1(double a, long n);
        static double _generate_harmonic_gt1(double a, long n);
};

#endif