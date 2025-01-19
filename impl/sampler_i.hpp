#ifndef SAMPLER_I_HPP
#define SAMPLER_I_HPP

class sampler_i {
    public:
        sampler_i(long range_, double skew_, long seed_) : range(range_), skew(skew_), seed(seed_) {};
        
        virtual ~sampler_i() = default;
        virtual long sample() = 0;
    protected:
        long range;
        double skew;
        long seed;
};

#endif