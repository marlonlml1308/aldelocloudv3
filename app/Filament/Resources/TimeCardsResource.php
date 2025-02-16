<?php

namespace App\Filament\Resources;

use App\Filament\Resources\TimeCardsResource\Pages;
use App\Filament\Resources\TimeCardsResource\RelationManagers;
use App\Models\Employees;
use App\Models\Timecards;
use Carbon\Carbon;
use Filament\Forms;
use Filament\Forms\Form;
use Filament\Resources\Resource;
use Filament\Tables;
use Filament\Tables\Enums\FiltersLayout;
use Filament\Tables\Filters\SelectFilter;
use Filament\Tables\Filters\Filter;
use Filament\Tables\Table;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\SoftDeletingScope;
use Livewire\Attributes\Layout;
use pxlrbt\FilamentExcel\Actions\Tables\ExportBulkAction;

use function Laravel\Prompts\select;

class TimeCardsResource extends Resource
{
    protected static ?string $model = Timecards::class;
    protected static ?string $navigationGroup = 'Empleados';
    protected static ?string $navigationIcon = 'heroicon-o-calendar-date-range';

    public static function form(Form $form): Form
    {
        return $form
            ->schema([
                //
                Forms\Components\Select::make('employeeid')->label('Cargo')
                ->required()
                ->relationship(name: 'Employees', titleAttribute: 'jobtitletext'),
            ]);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                //
                Tables\Columns\TextColumn::make('branch.branch')->label('Sucursal')
                ->sortable()
                ->disabledClick(),
                Tables\Columns\TextColumn::make('employees.fullname')
                ->label('Empleado')
                ->disabledClick(),
                // ->sortable(),
                // ->searchable(query: function (Builder $query, string $search): Builder {
                //     return $query->whereHas('employees', function ($q) use ($search) {
                //         $q->where('firstname', 'like', "%{$search}%")
                //           ->orWhere('lastname', 'like', "%{$search}%");
                //     });
                // }),
                Tables\Columns\TextColumn::make('workdate')->date()->label('Fecha entrada'),
                Tables\Columns\TextColumn::make('clockintime')
                ->label('Hora de Entrada')
                ->dateTime('h:i A') // Formato 12 horas con AM/PM
                ->sortable()
                ->disabledClick(),
                Tables\Columns\TextColumn::make('clockouttime')
                ->label('Hora de Salida')
                ->dateTime('h:i A') // Formato 12 horas con AM/PM
                ->sortable()
                ->disabledClick(),
                Tables\Columns\TextColumn::make('totalworkminutes')
                ->label('Total Horas')
                ->formatStateUsing(fn ($state) => $state !== null ? number_format($state / 60, 2) : '0.00')
                ->disabledClick()
                ->sortable(),
            ])
            ->filters([
                SelectFilter::make('Sucursal')
                    ->relationship('branch','branch')
                    ->searchable()
                    ->preload(),
                Filter::make('workdate')
                ->form([
                    Forms\Components\DatePicker::make('Fecha de Inicio'),
                    Forms\Components\DatePicker::make('Fecha de Fin'),
                ])
                ->query(function (Builder $query, array $data): Builder {
                    return $query
                        ->when(
                            $data['Fecha de Inicio'],
                            fn (Builder $query, $date): Builder => $query->whereDate('workdate', '>=', $date),
                        )
                        ->when(
                            $data['Fecha de Fin'],
                            fn (Builder $query, $date): Builder => $query->whereDate('workdate', '<=', $date),
                        );
                    })->columnSpan(2)->columns(2),
                Filter::make('employee')
                ->form([
                    Forms\Components\Select::make('employeeid') // Asegurar que coincide con la base de datos
                        ->label('Empleado')
                        ->searchable()
                        ->options(function () {
                            return Employees::all()->mapWithKeys(function ($employee) {
                                return [$employee->id => $employee->firstname . ' ' . $employee->lastname];
                            });
                        })
                ])
                ->query(fn (Builder $query, array $data): Builder =>
                    $query->when(
                        isset($data['employeeid']) && !empty($data['employeeid']),
                        fn (Builder $query) => $query->where('employeeid', $data['employeeid']) // Cambio de 'employee_id' a 'employeeid'
                    )
                ),
            ], layout: FiltersLayout::AboveContent)->filtersFormColumns(4)
            ->actions([
                // Tables\Actions\EditAction::make(),
            ])
            ->bulkActions([
                // Tables\Actions\BulkActionGroup::make([
                //     // Tables\Actions\DeleteBulkAction::make(),
                // ]),
                ExportBulkAction::make(),
            ]);
    }

    public static function getRelations(): array
    {
        return [
            //
        ];
    }

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListTimeCards::route('/'),
            'create' => Pages\CreateTimeCards::route('/create'),
            'edit' => Pages\EditTimeCards::route('/{record}/edit'),
        ];
    }
    public static function getModelLabel(): string
    {
        return __(key: 'Turno');
    }
    public static function getPluralModelLabel(): string
    {
        return __(key: 'Turnos');
    }
}
