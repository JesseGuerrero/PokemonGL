class ShaderConverter {
    constructor(shaderPath = 'static/shaders/') {
        this.shaderPath = shaderPath;
        this.shaders = new Map();
    }

    // Load a single shader file
    async loadShader(filename) {
        try {
            const response = await fetch(this.shaderPath + filename);
            if (!response.ok) {
                throw new Error(`Failed to load ${filename}: ${response.status}`);
            }
            const content = await response.text();
            const baseName = filename.split('.')[0]; // Get name without extension

            // Create script tag
            const script = document.createElement('script');
            script.id = `${baseName}-shader`;
            script.type = 'x-shader/x-glsl';
            script.textContent = content;

            // Add to head
            document.head.appendChild(script);

            // Store reference
            this.shaders.set(baseName, content);

            console.log(`✓ Loaded shader: ${baseName}`);
            return content;
        } catch (error) {
            console.error(`Error loading shader ${filename}:`, error);
            throw error;
        }
    }

    // Load multiple shaders
    async loadShaders(filenames) {
        const promises = filenames.map(filename => this.loadShader(filename));
        return Promise.all(promises);
    }

    // Get shader source by base name
    getShader(baseName) {
        const element = document.getElementById(`${baseName}-shader`);
        return element ? element.textContent : null;
    }
}

// Global instance for easy access
const shaderConverter = new ShaderConverter();

// Simple usage function
async function loadShadersFromFiles(filenames) {
    await shaderConverter.loadShaders(filenames);

    // Return easy access object
    const shaders = {};
    filenames.forEach(filename => {
        const baseName = filename.split('.')[0];
        shaders[baseName] = shaderConverter.getShader(baseName);
    });

    return shaders;
}