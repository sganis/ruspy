
use pyo3::prelude::*;
use std::path::PathBuf;

fn main() -> PyResult<()> {
    let mut exedir = std::env::current_exe()?;
    exedir.pop();
    println!("exedir: {}", exedir.display());
    let curdir = std::env::current_dir()?;
    println!("curdir: {}", curdir.display());

    if let Some(path) = std::env::var_os("PATH") {
        let mut paths = std::env::split_paths(&path).collect::<Vec<_>>();

        paths.push(PathBuf::from(format!("{}", curdir.display())));
        paths.push(PathBuf::from(format!("{}/lib", curdir.display())));
        
        paths.push(PathBuf::from(format!("{}", exedir.display())));
        paths.push(PathBuf::from(format!("{}/lib", exedir.display())));
        
        let new_path = std::env::join_paths(paths).unwrap();
        std::env::set_var("PATH", &new_path);
        //println!("new path: {:?}", new_path);
    }

    Python::with_gil(|py| {        
        

        let sys = py.import_bound("sys")?;
        let version: String = sys.getattr("version")?.extract()?;        
        println!("I'm Python {}", version);
        
        let syspath = sys.getattr("path")?;
        let append = syspath.getattr("append")?;

        append.call1((curdir.clone(),))?;
        append.call1((format!("{}/app", curdir.display()),))?;
        //append.call1((format!("{}/lib/python310.zip", curdir.display()),))?;
        append.call1((format!("{}/lib", curdir.display()),))?;
        
        append.call1((exedir.clone(),))?;
        append.call1((format!("{}/app", exedir.display()),))?;
        //append.call1((format!("{}/lib/python310.zip", exedir.display()),))?;
        append.call1((format!("{}/lib", exedir.display()),))?;
        

        let app: Py<PyAny> = py.import_bound("app")?.getattr("main")?.into();
        app.call0(py)?;        
        
        Ok(())
    })
}