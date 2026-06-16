# Recetario PAU Matematicas

## Sistemas segun el determinante

Para un sistema cuadrado \(AX=b\):

- Si \(\det(A)\ne 0\) => SCD
- Si \(\det(A)=0\): si \(\operatorname{rg}(A)=\operatorname{rg}(A\mid b)\) => SCI; si no, SI

## Rango por menores

- Menor de orden \(n\) distinto de \(0\) => \(\operatorname{rg}(A)\ge n\)
- Menor de orden \(n\) igual a \(0\) => no concluye
- Todos los menores de orden \(n\) iguales a \(0\) => \(\operatorname{rg}(A)<n\)

## Coseno del angulo entre dos vectores

- Si \(\vec u\) y \(\vec v\) son dos vectores no nulos: \(\cos(\alpha)=\frac{\vec u\cdot\vec v}{\lVert\vec u\rVert\,\lVert\vec v\rVert}\)
- Producto escalar en 3D: \(\vec u\cdot\vec v=u_1v_1+u_2v_2+u_3v_3\)
- Modulo: \(\lVert\vec u\rVert=\sqrt{u_1^2+u_2^2+u_3^2}\)
- Si \(\vec u\cdot\vec v=0\) => vectores perpendiculares

## Geometría Espacios Vectoriales

- Distancia de un punto a un plano. Si \(P(x_0,y_0,z_0)\) y \(\pi: Ax+By+Cz+D=0\), entonces:
  \[
  d(P,\pi)=\frac{|Ax_0+By_0+Cz_0+D|}{\sqrt{A^2+B^2+C^2}}
  \]

## Paridad de una funcion

- \(f(-x)=f(x)\) => par
- \(f(-x)=-f(x)\) => impar
- Si no, ni par ni impar

## Limites

- Sustituir primero; si sale numero, fin
- \(\frac{0}{0}\) => factorizar y simplificar; con raices, conjugado
- \(\frac{\infty}{\infty}\) racional => comparar grados: \(g_N<g_D\) da \(0\), \(g_N=g_D\) da cociente coef., \(g_N>g_D\) da \(\pm\infty\)
- \(\infty-\infty\) => comun denominador o conjugado
- \(0\cdot\infty\) => pasar a cociente
- \(\frac{a}{0}\) (\(a\ne 0\)) => laterales y signos: \(\pm\infty\)
- \(x\to+\infty\): \(\sqrt{x^2}=x\); \(x\to-\infty\): \(\sqrt{x^2}=-x\)
- Potencias raras (\(1^\infty\), \(0^0\), \(\infty^0\)) => tomar logaritmos
- Crecimiento: \(e^x\) gana a potencias; potencias ganan a \(\ln x\)
- Basico: \(\lim_{x\to 0}\frac{\sin x}{x}=1\)

## Recta tangente

- A \(f\) en \(x=a\): \(y=f(a)+f'(a)(x-a)\)

## Probabilidad: sucesos y complementarios

-  \(P(\bar A)=1-P(A)\)
- \(P(A\cup B)=P(A)+P(B)-P(A\cap B)\)
- Si \(A\) y \(B\) son incompatibles (rcda.: dado => en la misma tirada, sacar un 3 , sacar un 5): \(P(A\cap B)=0\) y \(P(A\cup B)=P(A)+P(B)\) 
-  \(P(\bar A\cap \bar B)=1-P(A\cup B)\)
-  \(P(\overline{A\cup B}) = P(\overline A\cap \overline B)\)
- Solo uno de los dos: \(P(A\cap \bar B)+P(B\cap \bar A)=P(A)+P(B)-2P(A\cap B)\)
- Siempre: \(P(A\cap B)=P(A)+P(B)-P(A\cup B)\)
- \(A\) y \(B\) independientes: \(P(A\cap B)=P(A)P(B)\)

## Tabla Venn para dos sucesos

\[
\begin{array}{c|c c c|c c}
 & B & + & \bar B & = & \text{Total} \\
\hline
A & P(A\cap B) & + & P(A\cap \bar B) & = & P(A) \\
+ & + & & + & & + \\
\bar A & P(\bar A\cap B) & + & P(\bar A\cap \bar B) & = & P(\bar A) \\
\hline
= & = & & = & &  \\
\text{Total} & P(B) & + & P(\bar B) & = & 1
\end{array}
\]

## Probabilidad condicionada, total y Bayes

- Probabilidad condicionada: \(P(A\mid B)=\frac{P(A\cap B)}{P(B)}\)
- \(P(\bar A\mid B)= 1- P(A\mid B)  \)
- Probabilidad total con \(B,\bar B\): \(P(A)=P(A\mid B)P(B)+P(A\mid \bar B)P(\bar B)\)
- Probabilidad total con particion \(B_1,\ldots,B_n\): \(P(A)=\sum_i P(A\mid B_i)P(B_i)\)
- Bayes: \(P(B_j\mid A)=\frac{P(A\mid B_j)P(B_j)}{\sum_i P(A\mid B_i)P(B_i)}\)

## Binomial

- Se usa cuando hay \(n\) repeticiones independientes, dos resultados posibles y probabilidad de exito constante \(p\)
- Si \(X\sim B(n,p)\): \(P(X=k)=\binom{n}{k}p^k(1-p)^{n-k}\)
- Como mucho \(r\) exitos: \(P(X\le r)=\sum_{k=0}^r \binom{n}{k}p^k(1-p)^{n-k}\)
- Al menos \(r\) exitos: \(P(X\ge r)=1-P(X\le r-1)\)
- Media y desviacion tipica: \(\mu=np\), \(\sigma=\sqrt{np(1-p)}\)

## Normal

- Si \(X\sim N(\mu,\sigma)\), tipificar: \(Z=\frac{X-\mu}{\sigma}\sim N(0,1)\)
- \(P(a\le X\le b)=P\left(\frac{a-\mu}{\sigma}\le Z\le \frac{b-\mu}{\sigma}\right)\)
- Simetria: \(P(Z\le -z)=1-P(Z\le z)\)
- Intervalo central: \(P(-z\le Z\le z)=2P(Z\le z)-1\)

## Intervalo de confianza para una media con \(\sigma\) conocida

- Intervalo: \(\left(\bar x-z_{\alpha/2}\frac{\sigma}{\sqrt n},\bar x+z_{\alpha/2}\frac{\sigma}{\sqrt n}\right)\)
- Error maximo: \(E=z_{\alpha/2}\frac{\sigma}{\sqrt n}\)
- Tamano minimo de muestra para error \(E\): \(n\ge \left(\frac{z_{\alpha/2}\sigma}{E}\right)^2\); redondear siempre hacia arriba
- Valores habituales: 90 % => \(z_{\alpha/2}=1.645\); 95 % => \(1.96\); 97 % => \(2.17\); 99 % => \(2.575\)
