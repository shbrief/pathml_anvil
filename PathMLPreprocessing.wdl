workflow PathMLPreprocessing {
	call StainNormalizationHE
	meta {
		author: "Sehyun Oh"
        email: "shbrief@gmail.com"
        description: "PathML: H&E Stain Deconvolution and Color Normalization"
    }
}

task StainNormalizationHE {
    File image_svs
    String sampleName
  
  command {
    python3 <<CODE
    
    import numpy as np
    import matplotlib.pyplot as plt
    
    from pathml.core import HESlide
    from pathml.preprocessing import StainNormalizationHE
    
    fontsize = 20
    
    wsi = HESlide("${image_svs}")
    region = wsi.slide.extract_region(location = (900, 800), size = (500, 500))
    
    plt.imshow(region)
    plt.title("Original image", fontsize=fontsize)
    plt.gca().set_xticks([])
    plt.gca().set_yticks([])
    plt.savefig("${sampleName}_original.png", bbox_inches = "tight")
        
    fig, axarr = plt.subplots(nrows=2, ncols=3, figsize=(10, 7.5))
        
    for i, method in enumerate(["macenko", "vahadane"]):
        for j, target in enumerate(["normalize", "hematoxylin", "eosin"]):
            # initialize stain normalization object
            normalizer = StainNormalizationHE(target = target, stain_estimation_method = method)
            # apply on example image
            im = normalizer.F(region)
            # plot results
            ax = axarr[i, j]
            ax.imshow(im)
            if j == 0:
                ax.set_ylabel(method, fontsize=fontsize)
            if i == 0:
                ax.set_title(target, fontsize = fontsize)
        
    for a in axarr.ravel():
        a.set_xticks([])
        a.set_yticks([])
    
    plt.tight_layout()
    plt.savefig("${sampleName}_preprocessed.png", bbox_inches = "tight")
        
    CODE
  }
  
  output {
    File original = "${sampleName}_original.png"
    File preprocessed = "${sampleName}_preprocessed.png"
  }
  
  runtime {
    docker: "quay.io/shbrief/pathml_anvil"
    cpu: 4
      memory: "16 GB"
      disks: "local-disk 5 SSD"
  }
}

