import { classy } from '@/util/css'

import classes from './Checkbox.module.css'

type CheckboxProps = {
  label?: string
  tip?: string
  checked?: boolean
  disabled?: boolean
  onClick?: () => void
}

export const Checkbox = ({ label, tip, checked, disabled, onClick }: CheckboxProps) => {
  const rootClasses = classy(classes.Checkbox, {
    [classes.disabled]: disabled,
  })

  return (
    <div className={rootClasses}>
      <button
        className={classes.button}
        disabled={disabled}
        onClick={onClick}
      >
        {checked ? (
          <span className={classes.indicator}>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="9"
              height="9"
              viewBox="0 0 9 9"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                clipRule="evenodd"
                d="M8.535** 0.622**C8.882** 0.849446 8.979** 1.3142 8.753** 1.660**L4.5083 8.1599C4.388** 8.343** 4.193** 8.4655 3.9764 8.493**C3.758** 8.521** 3.539** 8.453** 3.3772 8.305**L0.616113 5.807**C0.308959 5.529** 0.285246 5.055** 0.563148 4.748**C0.841** 4.441** 1.315** 4.417** 1.622** 4.695**L3.732** 6.604**L7.497** 0.840706C7.723** 0.493916 8.188** 0.396414 8.535** 0.622**Z"
              ></path>
            </svg>
          </span>
        ) : null}
      </button>
      {label ? (
        <span
          className={classes.label}
          onClick={onClick}
        >
          {label}
        </span>
      ) : null}
      {tip ? <div className={classes.tip}>{tip}</div> : null}
    </div>
  )
}
