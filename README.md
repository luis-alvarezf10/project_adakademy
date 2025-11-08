<header>
    <h1>🚀 Think It - Sistema de Gestión Escolar</h1>
</header>

<hr>

<section id="descripcion">
    <h2>Descripción del Proyecto</h2>
    <p><strong>Think It</strong> es una aplicación web integral diseñada para la <strong>gestión de notas, asignaturas, profesores y alumnos</strong> en un entorno escolar. Desarrollada como proyecto final de curso de desarrollo web con <strong>Django</strong>, busca optimizar la administración académica, proporcionando una interfaz clara y funcional para los distintos usuarios del sistema.</p>
    <p>Este proyecto fue desarrollado por Luis Álvarez, José Castillo, Angel Romero un equipo de estudiantes como demostración de nuestras habilidades en el <em>backend</em> (Django, Python) y el <em>frontend</em> (HTML, CSS, JavaScript) siguiendo metodologías de desarrollo ágil.</p>
</section>

<hr>

<section id="caracteristicas">
    <h2>✨ Características Principales</h2>
    <ul>
        <li><strong>👤 Gestión de Usuarios y Roles:</strong> Diferentes niveles de acceso para <strong>Profesores</strong> y <strong>Alumnos</strong>.</li>
        <li><strong>🎓 Gestión de Alumnos:</strong> Inscripción, información detallada y seguimiento del rendimiento.</li>
        <li><strong>📝 Gestión de Calificaciones:</strong> Carga y visualización de notas por periodo/evaluación.</li>
        <li><strong>📈 Dashboard Informativo:</strong> Resumen visual del estado académico.</li>
    </ul>
</section>

<hr>

<section id="tecnologias">
    <h2>🛠️ Tecnologías Utilizadas</h2>
    <p>El proyecto Think It fue construido utilizando las siguientes herramientas y <em>frameworks</em>:</p>
    <h3>Backend</h3>
    <ul>
        <li><strong>Python:</strong> Lenguaje de programación principal.</li>
        <li><strong>Django:</strong> Framework web principal.</li>
        <li><strong>Base de Datos:</strong> **SQLite** (por defecto).</li>
    </ul>
    <h3>Frontend</h3>
    <ul>
        <li><strong>HTML5</strong></li>
        <li><strong>CSS3</strong></li>
        <li><strong>JavaScript</strong></li>
        <li><strong>Tailwind css:</strong> Framework web para estilos</li>
    </ul>
    <h3>Herramientas de Desarrollo</h3>
    <ul>
        <li><strong>Git / GitHub:</strong> Control de versiones.</li>
        <li><strong>Python Anywhere:</strong> Despliegue de pagina web.</li>
        <li><strong>Trello:</strong> Gestión de actividades a realizar en el proyecto.</li>
        <li><strong>Whimsical:</strong> Diseño diagramas de modelos de entidad relacional y de casos de uso.</li>
    </ul>
</section>

<hr>

<section id="instalacion">
    <h2>💻 Instalación y Ejecución Local</h2>
    <p>Sigue estos pasos para poner en marcha el proyecto en tu máquina local.</p>
    <h3>1. Clona el Repositorio</h3>
    <div>
        
        git clone https://github.com/luis-alvarezf10/project_adakademy
        cd project_adakademy

</div>
    <h3>2. Configura el Entorno Virtual</h3>
    <p>Es fundamental trabajar dentro de un entorno virtual para aislar las dependencias del proyecto.</p>
    <div>
    
        # Para Windows

        python -m venv venv
        venv\Scripts\activate

        # Para macOS/Linux
        python3 -m venv venv
        source venv/bin/activate
  </div>
    <h3>3. Instala las Dependencias</h3>
    <p>Instala todas las librerías necesarias desde el archivo <code>requirements.txt</code>.</p>
    <div>
        <pre><code>pip install -r requirements.txt</code></pre>
    </div>
    <h3>4. Configuración de la Base de Datos y Migraciones</h3>
    <p>Aplica las migraciones iniciales para crear la estructura de la base de datos.</p>
    <div>
        <pre><code>python manage.py migrate</code></pre>
    </div>
    <h3>5. Crear un Superusuario (Administrador)</h3>
    <p>Necesitarás un usuario administrador para acceder al <em>Django Admin</em> y gestionar el sistema inicialmente.</p>
    <div>
        <pre><code>python manage.py createsuperuser</code></pre>
    </div>
    <p><em>(Sigue las indicaciones para establecer un nombre de usuario y contraseña)</em></p>
    <h3>6. Ejecuta el Servidor de Desarrollo</h3>
    <div>
        <pre><code>python manage.py runserver</code></pre>
    </div>
    <p>El sistema estará accesible en tu navegador en: <code>http://127.0.0.1:8000/</code></p>
</section>

<hr>

<section id="equipo">
    <h2>👥 Equipo de Desarrollo</h2>
    <p>Este proyecto fue desarrollado por:</p>
    <table>
        <thead>
            <tr>
                <th>n</th>
                <th>Nombre</th>
                <th>Contacto (Opcional)</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>1</td>
                <td>Luis Alvarez</td>
                <td>...</td>
            </tr>
            <tr>
                <td>2</td>
                <td>José Castillo</td>
                <td>...</td>
            </tr>
            <tr>
                <td>3</td>
                <td>Angel Romero</td>
                <td>...</td>
            </tr>
            <tr>
                <td>...</td>
                <td>...</td>
                <td>...</td>
            </tr>
        </tbody>
    </table>
</section>

<hr>

<section id="licencia">
    <h2>📄 Licencia</h2>
    <p>Este proyecto está bajo la licencia.</p>
</section>
