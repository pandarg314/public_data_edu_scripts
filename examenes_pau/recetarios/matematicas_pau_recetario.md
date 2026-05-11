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

## Probabilidad condicionada

- Probabilidad de que ocurra \(A\) sabiendo que ha ocurrido \(B\): \(P(A\mid B)=\frac{P(A\cap B)}{P(B)}\)
- Solo se puede usar si \(P(B)\ne 0\)
- Equivalente util: \(P(A\cap B)=P(B)P(A\mid B)\)
