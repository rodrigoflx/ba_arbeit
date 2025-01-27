use pyo3::prelude::*;
use rand::prelude::*; // Import RNG traits
use rand::distributions::Distribution; // Required for `sample`
use zipf::ZipfDistribution;

/// A struct that wraps ZipfDistribution for Python
#[pyclass]
struct PyZipf {
    inner: ZipfDistribution,
}

#[pymethods]
impl PyZipf {
    #[new]
    fn new(size: usize, exponent: f64) -> PyResult<Self> {
        // Handle any errors when creating the Zipf distribution
        match ZipfDistribution::new(size, exponent) {
            Ok(dist) => Ok(Self { inner: dist }),
            Err(_) => Err(pyo3::exceptions::PyValueError::new_err(
                "Failed to create ZipfDistribution. Ensure size > 0 and exponent > 1.",
            )),
        }
    }

    fn sample(&self) -> usize {
        let mut rng = rand::thread_rng();
        self.inner.sample(&mut rng)
    }

    fn benchmark(&self, samples: usize) -> usize {
        let mut rng = rand::thread_rng();
        let start = std::time::Instant::now();
        
        for _ in 0..samples {
            self.inner.sample(&mut rng);
        }
        
        let duration = start.elapsed();
        duration.as_millis() as usize
    }
}

/// Python module definition
#[pymodule]
fn zipf_rust(m : &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyZipf>()?;
    Ok(())
}
